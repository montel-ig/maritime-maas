import logging
from collections import defaultdict
from datetime import datetime
from math import isnan
from timeit import default_timer as timer

import gtfs_kit
from django.contrib.gis.db import models
from django.contrib.gis.geos import LineString, Point
from django.db import transaction
from django.utils import timezone

from gtfs.importers.gtfs_feed_reader import GTFSFeedReader
from gtfs.models import (
    Agency,
    Departure,
    Fare,
    FareRiderCategory,
    FareRule,
    FeedInfo,
    RiderCategory,
    Route,
    Shape,
    Stop,
    StopTime,
    Trip,
)


class GTFSFeedImporterError(Exception):
    pass


class GTFSFeedImporter:
    MODELS_AND_GTFS_KIT_ATTRIBUTES = (
        (Agency, "agency"),
        (Route, "routes"),
        (Trip, "trips"),
        (Stop, "stops"),
        (StopTime, "stop_times"),
        (Fare, "fare_attributes"),
        (FareRule, "fare_rules"),
        (RiderCategory, "rider_categories"),
        (FareRiderCategory, "fare_rider_categories"),
        (FeedInfo, "feed_info"),
    )

    TRANSLATION_MAPPING = [
        "table_name",
        "field_name",
        "language",
        "translation",
        "record_id",
    ]

    TRANSLATIONS = "translations"

    # Mapping from GTFSModel field to GTFS field.
    # GTFS field can contain multiple values.
    FIELD_MAPPING = {
        FeedInfo: {
            "publisher_name": "feed_publisher_name",
            "publisher_url": "feed_publisher_url",
            "lang": "feed_lang",
            "default_lang": "default_lang",
            "start_date": "feed_start_date",
            "end_date": "feed_end_date",
            "version": "feed_version",
            "contact_email": "feed_contact_email",
        },
        Agency: {
            "source_id": "agency_id",
            "name": "agency_name",
            "url": "agency_url",
            "timezone": "agency_timezone",
            "logo_url": "agency_logo_url",
        },
        Trip: {
            "source_id": "trip_id",
            "route_id": "route_id",
            "direction_id": "direction_id",
            "wheelchair_accessible": "wheelchair_accessible",
            "bikes_allowed": "bikes_allowed",
            "shape_id": "shape_id",
            "block_id": "block_id",
        },
        Route: {
            "source_id": "route_id",
            "agency_id": "agency_id",
            "short_name": "route_short_name",
            "long_name": "route_long_name",
            "desc": "route_desc",
            "type": "route_type",
            "sort_order": "route_sort_order",
            "capacity_sales": "capacity_sales",
        },
        Stop: {
            "source_id": "stop_id",
            "name": "stop_name",
            "desc": "stop_desc",
            "tts_name": "tts_stop_name",
            "point": ("stop_lat", "stop_lon"),
            "wheelchair_boarding": "wheelchair_boarding",
        },
        StopTime: {
            "trip_id": "trip_id",
            "stop_id": "stop_id",
            "arrival_time": "arrival_time",
            "departure_time": "departure_time",
            "stop_sequence": "stop_sequence",
            "stop_headsign": "stop_headsign",
            "timepoint": "timepoint",
        },
        Fare: {
            "source_id": "fare_id",
            "agency_id": "agency_id",
            "price": "price",
            "currency_type": "currency_type",
            "payment_method": "payment_method",
            "transfers": "transfers",
            "name": "fare_name",
            "description": "fare_description",
            "instructions": "fare_instructions",
        },
        FareRule: {
            "fare_id": "fare_id",
            "route_id": "route_id",
        },
        RiderCategory: {
            "source_id": "rider_category_id",
            "name": "rider_category_name",
            "description": "rider_category_description",
        },
        FareRiderCategory: {
            "fare_id": "fare_id",
            "rider_category_id": "rider_category_id",
            "price": "price",
            "currency_type": "currency_type",
        },
    }

    def __init__(
        self,
        object_creation_batch_size=2000,  # Stetson-Harrison method
        logger=None,
    ):
        self.object_creation_batch_size = object_creation_batch_size
        self.logger = logger or logging.getLogger(__name__)
        self.feed_reader = GTFSFeedReader()
        # IDs of all created objects that have a source ID are cached so that we can
        # use them to populate foreign key fields of later imported object types
        self.id_cache = defaultdict(dict)

        # Save feed_lang, when looping through models we need access to this value
        self.feed_lang = ""

    def run(self, feed, skip_validation=False):
        feed_name = feed.name or "<no name>"
        self.logger.info(
            f'Importing GTFS feed "{feed_name}" from "{feed.url_or_path}"...'
        )

        self.id_cache.clear()
        start_time = timer()

        self.logger.info("Reading data...")
        try:
            gtfs_feed = self.feed_reader.read_feed(feed.url_or_path)
        except ValueError as e:
            raise GTFSFeedImporterError(f"Error reading GTFS feed: {str(e)}") from e

        if not skip_validation:
            self.logger.debug("Validating data...")
            if results := self.feed_reader.validate(gtfs_feed):
                if any(r[0] == "error" for r in results):
                    message = f"Validation errors and warnings: {results}"
                    self.logger.error(message)
                    raise GTFSFeedImporterError(message)
                else:
                    self.logger.debug(f"Validation warnings: {results}")

        with transaction.atomic():
            self._delete_existing_gtfs_objects(feed)

            self._import_shapes(feed, gtfs_feed)
            for model, gtfs_attribute in self.MODELS_AND_GTFS_KIT_ATTRIBUTES:
                self._import_model(feed, model, getattr(gtfs_feed, gtfs_attribute))

            self._create_departures(gtfs_feed)

            feed.fingerprint = self.feed_reader.get_feed_fingerprint(feed)

            translation_list = self._form_translation_list(
                getattr(gtfs_feed, self.TRANSLATIONS)
            )

            for model, _gtfs_attribute in self.MODELS_AND_GTFS_KIT_ATTRIBUTES:
                self._add_translations(model, translation_list, feed)

            feed.imported_at = timezone.now()
            # the feed's name will also get autopopulated here if feed info is available
            feed.save()

        end_time = timer()
        feed_name = feed.name or "<no name>"
        self.logger.info(
            f'Successfully imported GTFS feed "{feed_name}" from "{feed.url_or_path}" '
            f"in {end_time - start_time:.2f} secs!"
        )

    def _delete_existing_gtfs_objects(self, feed):
        models_to_delete = [Shape] + [m[0] for m in self.MODELS_AND_GTFS_KIT_ATTRIBUTES]
        for model in models_to_delete:
            self.logger.debug(
                f"Deleting existing {model._meta.verbose_name_plural}"
                f"{' and departures' if model == Trip else ''}..."
            )
            model.objects.filter(feed=feed).delete()

    def _import_shapes(self, feed, gtfs_feed):
        gtfs_data = gtfs_feed.shapes
        num_of_rows = len(gtfs_data) if gtfs_data is not None else 0

        if num_of_rows:
            self.logger.info(f"Importing {num_of_rows} shape points...")
        else:
            self.logger.info("No shapes.")
            return

        grouped = gtfs_data.sort_values(by="shape_pt_sequence").groupby("shape_id")
        num_of_shapes = len(grouped)

        for num_of_processed, gtfs_row in enumerate(
            grouped[["shape_pt_lat", "shape_pt_lon"]], 1
        ):
            coordinates = gtfs_row[1][["shape_pt_lat", "shape_pt_lon"]]
            geometry = LineString(
                [(c.shape_pt_lon, c.shape_pt_lat) for c in coordinates.itertuples()]
            )
            shape = Shape.objects.create(
                feed=feed, source_id=gtfs_row[0], geometry=geometry
            )
            self.id_cache[Shape].update({shape.source_id: shape.id})
            if (
                num_of_processed % self.object_creation_batch_size == 0
                or num_of_processed >= num_of_shapes
            ):
                self.logger.debug(
                    f"Processed {num_of_processed}/{num_of_shapes} shapes"
                )

    def _import_model(self, feed, model, gtfs_data):  # noqa: C901
        num_of_rows = len(gtfs_data) if gtfs_data is not None else 0
        plural_name = model._meta.verbose_name_plural

        if num_of_rows:
            self.logger.info(f"Importing {num_of_rows} {plural_name}...")
        else:
            self.logger.info(f"No {plural_name}")
            return

        try:
            translation_model = model.translations.rel.related_model
        except AttributeError:
            translation_model = None

        objs_to_create = []
        manually_created = []
        num_of_skipped = 0

        # gtfs_kit returns DataFrames and extra dataset uses list
        iterable_data = (
            gtfs_data if isinstance(gtfs_data, list) else gtfs_data.itertuples()
        )

        for num_of_processed, gtfs_row in enumerate(iterable_data, 1):
            creation_attributes = {}
            translation_attributes = {}

            # Populate object creation attributes using the mapping from model fields
            # to GTFS fields. How the values are converted between the two is
            # determined by the model field's type.
            for model_field_name, gtfs_field in self.FIELD_MAPPING[model].items():
                gtfs_value = (
                    getattr(gtfs_row, gtfs_field, None)
                    if isinstance(gtfs_field, str)
                    # when a model field is mapped to multiple GTFS fields build a
                    # list of their values
                    else [getattr(gtfs_row, f, None) for f in gtfs_field]
                )

                if translation_model and model_field_name in [
                    f.name for f in translation_model._meta.get_fields()
                ]:
                    model_field = translation_model._meta.get_field(model_field_name)
                    translation_attributes[model_field_name] = self._convert_value(
                        gtfs_value, model_field, gtfs_field
                    )
                else:
                    model_field = model._meta.get_field(model_field_name)
                    if (
                        converted_value := self._convert_value(
                            gtfs_value, model_field, gtfs_field
                        )
                    ) is not None:
                        creation_attributes[model_field_name] = converted_value

            new_obj = model(feed_id=feed.id, **creation_attributes)
            if hasattr(model, "populate_api_id"):
                new_obj.populate_api_id()

            if model == FeedInfo:
                self.feed_lang = creation_attributes.get("lang")

            if translation_model is not None:
                new_obj.set_current_language(self.feed_lang)
                for key in translation_attributes:
                    setattr(new_obj, key, translation_attributes[key])
                new_obj.save()
                manually_created.append(new_obj)
            else:
                objs_to_create.append(new_obj)

            if (
                num_of_processed % self.object_creation_batch_size == 0
                or num_of_processed >= num_of_rows  # yes this should never be GT
            ):
                created_objs = model.objects.bulk_create(objs_to_create)

                # update ID cache
                if "source_id" in creation_attributes:
                    obj_list = created_objs or manually_created
                    self.id_cache[model].update({o.source_id: o.id for o in obj_list})

                objs_to_create = []
                manually_created = []

                self.logger.debug(
                    f"Processed {num_of_processed}/{num_of_rows} {plural_name}"
                )
                if num_of_processed >= num_of_rows and num_of_skipped:
                    self.logger.info(f"Skipped {num_of_skipped} {plural_name}")

    def _create_departures(self, gtfs_feed):
        self.logger.info("Creating departures...")

        self.logger.debug("Computing trip activity...")
        dates = gtfs_kit.calendar.get_dates(gtfs_feed)
        trip_activities = gtfs_kit.compute_trip_activity(gtfs_feed, dates)

        num_of_activities = len(trip_activities)
        objs_to_create = []
        total_num_of_created = 0

        for index, trip_activity in trip_activities.iterrows():
            for date_str in trip_activity[trip_activity == 1].index:
                trip = self.id_cache[Trip][trip_activity["trip_id"]]
                trip_date = gtfs_kit.datestr_to_date(date_str)

                departure = Departure(trip_id=trip, date=trip_date)
                departure.populate_api_id()
                objs_to_create.append(departure)

                if len(objs_to_create) % self.object_creation_batch_size == 0:
                    Departure.objects.bulk_create(objs_to_create)
                    total_num_of_created += len(objs_to_create)
                    objs_to_create = []

            num_of_processed = int(index) + 1
            if (
                num_of_processed % self.object_creation_batch_size
            ) == 0 or num_of_processed >= num_of_activities:
                self.logger.debug(
                    f"Processed {num_of_processed}/{num_of_activities} trips"
                )

        total_num_of_created += len(objs_to_create)
        Departure.objects.bulk_create(objs_to_create)

        self.logger.debug(f"Created {total_num_of_created} departures")

    def _convert_value(self, gtfs_value, model_field, gtfs_field):
        if isinstance(model_field, models.ForeignKey):
            value = self._get_related_obj_id(model_field.related_model, gtfs_value)
            # empty agency_id should default to the only agency there (hopefully) is
            # in the feed
            if gtfs_field == "agency_id" and not value:
                value = self._get_default_agency_id()
            return value
        elif isinstance(model_field, models.DateField):
            return self._convert_date(gtfs_value)
        elif isinstance(model_field, models.PointField):
            return self._convert_point(gtfs_value)
        elif isinstance(model_field, models.IntegerField):
            return self._convert_int(gtfs_value)
        elif isinstance(model_field, models.CharField) or isinstance(
            model_field, models.TextField
        ):
            return self._convert_str(gtfs_value)
        else:
            # no conversion needed
            return gtfs_value

    def _get_related_obj_id(self, related_model, source_id):
        return self.id_cache[related_model].get(source_id)

    def _get_default_agency_id(self):
        agency_ids = self.id_cache[Agency].values()
        if len(agency_ids) != 1:
            raise GTFSFeedImporterError(
                f"Something fishy going on! Trying to use default agency but there "
                f"are {len(agency_ids)} agencies in the feed."
            )
        return next(iter(agency_ids))

    def _form_translation_list(self, gtfs_data):
        iterable_data = (
            gtfs_data if isinstance(gtfs_data, list) else gtfs_data.itertuples()
        )
        translations_list = []
        for _num_of_processed, gtfs_row in enumerate(iterable_data, 1):
            translation_fields = {}

            for gtfs_field in self.TRANSLATION_MAPPING:
                gtfs_value = getattr(gtfs_row, gtfs_field, None)
                translation_fields[gtfs_field] = self._convert_str(gtfs_value)
            translations_list.append(translation_fields)

        return translations_list

    def _add_translations(self, model, translations_list, feed):
        plural_name = model._meta.verbose_name_plural
        translations_for_model = [
            t
            for t in translations_list
            if t.get("table_name") == plural_name.replace(" ", "_")
        ]
        num_of_translations = len(translations_for_model)

        if num_of_translations == 0:
            return

        self.logger.info(
            f"Adding {num_of_translations} translations for {plural_name}..."
        )

        obj_list = model.objects.filter(feed=feed)

        model_fields = [*self.FIELD_MAPPING[model]]
        gtfs_fields = [*self.FIELD_MAPPING[model].values()]

        for trans in translations_for_model:
            obj = obj_list.get(source_id=trans.get("record_id"))
            field_name = trans.get("field_name", "")
            if field_name in gtfs_fields:
                index = gtfs_fields.index(field_name)
                model_field = model_fields[index]
                obj.set_current_language(trans.get("language"))
                setattr(obj, model_field, trans.get("translation"))
                obj.save()

    @staticmethod
    def _convert_date(gtfs_value):
        return datetime.strptime(gtfs_value, "%Y%m%d").date() if gtfs_value else None

    @staticmethod
    def _convert_point(gtfs_value):
        return Point(gtfs_value[1], gtfs_value[0])

    @staticmethod
    def _convert_int(gtfs_value):
        try:
            # if there are any empty values in the current column all of the column's
            # values have been converted to floats, hence the round()
            return round(gtfs_value)
        except (ValueError, TypeError):  # nan, None
            return None

    @staticmethod
    def _convert_str(gtfs_value):
        try:
            if isnan(gtfs_value):
                return ""
        except TypeError:
            return gtfs_value or ""
