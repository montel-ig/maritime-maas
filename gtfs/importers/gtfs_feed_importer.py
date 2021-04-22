import logging
from collections import defaultdict
from datetime import datetime, time
from math import isnan
from timeit import default_timer as timer

import gtfs_kit
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.db import transaction

from gtfs.importers.gtfs_feed_reader import GTFSFeedReader
from gtfs.models import (
    Agency,
    Fare,
    FareRiderCategory,
    FareRule,
    Feed,
    RiderCategory,
    Route,
    Stop,
    StopTime,
    Trip,
)
from gtfs.models.base import GTFSModelWithSourceID
from gtfs.models.departure import Departure


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
    )

    TRANSLATION_MAPPING = {
        'table_name': 'table_name',
        'field_name': 'field_name',
        'language': 'language',
        'translation': 'translation',
        'record_id': 'record_id'
    }

    # Mapping from GTFSModel field to GTFS field.
    # GTFS field can contain multiple values.
    FIELD_MAPPING = {
        Agency: {
            "source_id": "agency_id",
            "name": "agency_name",
            "url": "agency_url",
            "timezone": "agency_timezone",
        },
        Trip: {
            "source_id": "trip_id",
            "route_id": "route_id",
            "direction_id": "direction_id",
        },
        Route: {
            "source_id": "route_id",
            "agency_id": "agency_id",
            "short_name": "route_short_name",
            "long_name": "route_long_name",
            "type": "route_type",
        },
        Stop: {
            "source_id": "stop_id",
            "name": "stop_name",
            "point": ("stop_lat", "stop_lon"),
        },
        StopTime: {
            "trip_id": "trip_id",
            "stop_id": "stop_id",
            "arrival_time": "arrival_time",
            "departure_time": "departure_time",
            "stop_sequence": "stop_sequence",
            "stop_headsign": "stop_headsign",
        },
        Fare: {
            "source_id": "fare_id",
            "agency_id": "agency_id",
            "price": "price",
            "currency_type": "currency_type",
            "payment_method": "payment_method",
            "transfers": "transfers",
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

        # IDs of all created objects that have a source ID are cached so that we can
        # use them to populate foreign key fields of later imported object types
        self.id_cache = defaultdict(dict)

    def run(self, url_or_filename, skip_validation=False):
        self.logger.info(f'Importing a GTFS feed from "{url_or_filename}"...')
        self.id_cache.clear()
        feed_reader = GTFSFeedReader()
        start_time = timer()

        self.logger.info("Reading data...")
        gtfs_feed = feed_reader.read_feed(url_or_filename)

        """  
        if not skip_validation:
            self.logger.debug("Validating data...")
            results = feed_reader.validate(gtfs_feed)
            if results:
                self.logger.info("Validation errors:")
                self.logger.info(results)
                return
        """
        with transaction.atomic():
        # TODO just some temporary feed handling to get things rolling
            feed, _ = Feed.objects.get_or_create(name=url_or_filename)

            self._delete_existing_gtfs_objects(feed)

            for model, gtfs_attribute in self.MODELS_AND_GTFS_KIT_ATTRIBUTES:
                self._import_model(feed, model, getattr(gtfs_feed, gtfs_attribute))

            self._create_departures(gtfs_feed)

            translation_list = self._form_translation_list(getattr(gtfs_feed, 'translations'))

            for model, gtfs_attribute in self.MODELS_AND_GTFS_KIT_ATTRIBUTES:
                self._add_translations(model, translation_list)

            # Update the feed's updated_at. We might want to do something else here.
            feed.save()

            self.logger.debug("Committing...")

            end_time = timer()
            self.logger.info(
                f'Successfully imported a GTFS feed from "{url_or_filename}" in {end_time - start_time:.2f} secs!'
            )

    def _delete_existing_gtfs_objects(self, feed):
        for model, _ in self.MODELS_AND_GTFS_KIT_ATTRIBUTES:
            self.logger.debug(
                f"Deleting existing {model._meta.verbose_name_plural}"
                f"{' and departures' if model == Trip else ''}..."
            )
            model.objects.filter(feed=feed).delete()

    def _import_model(self, feed, model, gtfs_data):
        num_of_rows = len(gtfs_data) if gtfs_data is not None else 0
        plural_name = model._meta.verbose_name_plural

        if num_of_rows:
            self.logger.info(f"Importing {num_of_rows} {plural_name}...")
        else:
            self.logger.info(f"No {plural_name}")
            return

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
            try:
                translation_model = model.translations.rel.related_model
            except:
                translation_model = None

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

                if translation_model is not None and model_field_name in [f.name for f in translation_model._meta.get_fields()]:
                    model_field = translation_model._meta.get_field(model_field_name)
                    translation_attributes[model_field_name] = self._convert_value(
                        gtfs_value, model_field, gtfs_field
                    )
                else:
                    model_field = model._meta.get_field(model_field_name)
                    creation_attributes[model_field_name] = self._convert_value(
                        gtfs_value, model_field, gtfs_field
                    )

            new_obj = model(feed_id=feed.id, **creation_attributes)

            if issubclass(model, GTFSModelWithSourceID):
                new_obj.populate_api_id()

            if translation_model is not None:
                # TODO add here a way to use agency language
                new_obj.set_current_language('fi')
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
                    obj_list = created_objs if len(created_objs) > 0 else manually_created
                    self.id_cache[model].update(
                        {o.source_id: o.id for o in obj_list}
                    )

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
            num_of_processed = int(index) + 1
            if (num_of_processed % self.object_creation_batch_size) == 0:
                self.logger.debug(
                    f"Processed {num_of_processed}/{num_of_activities} trips"
                )

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
        elif isinstance(model_field, models.TimeField):
            return self._convert_time(gtfs_value)
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
        for num_of_processed, gtfs_row in enumerate(iterable_data, 1):
            translation_fields = {}

            for model_field_name, gtfs_field in self.TRANSLATION_MAPPING.items():
                gtfs_value = getattr(gtfs_row, gtfs_field, None)
                translation_fields[model_field_name] = self._convert_str(gtfs_value)
            translations_list.append(translation_fields)

        return translations_list

    def _add_translations(self, model, translations_list):
        plural_name = model._meta.verbose_name_plural
        translations_for_model = [t for t in translations_list if t.get('table_name') == plural_name]
        num_of_translations = len(translations_for_model)

        if num_of_translations == 0:
            return
        else:
            self.logger.info(f"Adding {num_of_translations} translations for {plural_name}...")

        for trans in translations_for_model:
            for model_field_name, gtfs_field in self.FIELD_MAPPING[model].items():
                if trans.get('field_name') == gtfs_field:
                    trans['field_name'] = model_field_name

        obj_list = model.objects.all()
        for obj in obj_list:
            for trans in translations_for_model:
                if trans.get('record_id') == obj.source_id:
                    obj.set_current_language(trans.get('language'))
                    setattr(obj, trans.get('field_name'), trans.get('translation'))
            obj.save()

    @staticmethod
    def _convert_date(gtfs_value):
        return datetime.strptime(gtfs_value, "%Y%m%d").date()

    @staticmethod
    def _convert_time(gtfs_time_value):
        # TODO THIS DOES NOT ACTUALLY WORK IN ALL SITUATIONS!
        # In GTFS it is possible for a time to go past midnight like 26:00:00.
        # It is probably not possible to support those with Django's TimeField which we
        # are using ATM. For now the times that go too far are just clipped.
        hours, mins, secs = map(int, gtfs_time_value.split(":"))
        if hours > 23:
            hours = 23
            mins = 59
            secs = 59
        return time(hours, mins, secs)

    @staticmethod
    def _convert_point(gtfs_value):
        return Point(gtfs_value[1], gtfs_value[0])

    @staticmethod
    def _convert_int(gtfs_value):
        try:
            return int(gtfs_value or 0)
        except ValueError:  # nan
            return None

    @staticmethod
    def _convert_str(gtfs_value):
        try:
            if isnan(gtfs_value):
                return ""
        except TypeError:
            return gtfs_value or ""
