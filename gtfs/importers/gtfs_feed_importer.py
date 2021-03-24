import logging
from collections import defaultdict
from datetime import datetime, time
from timeit import default_timer as timer

import gtfs_kit
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.db import transaction

from gtfs.models import (
    Agency,
    Calendar,
    CalendarDate,
    Fare,
    FareRule,
    Feed,
    Route,
    Stop,
    StopTime,
    Trip,
)


class GTFSFeedImporterError(Exception):
    pass


class GTFSFeedImporter:
    MODELS_AND_GTFS_KIT_ATTRIBUTES = (
        (Agency, "agency"),
        (Calendar, "calendar"),
        (CalendarDate, "calendar_dates"),
        (Route, "routes"),
        (Trip, "trips"),
        (Stop, "stops"),
        (StopTime, "stop_times"),
        (Fare, "fare_attributes"),
        (FareRule, "fare_rules"),
    )

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
            "calendar_id": "service_id",
            "route_id": "route_id",
        },
        Calendar: {
            "source_id": "service_id",
            "monday": "monday",
            "tuesday": "tuesday",
            "wednesday": "wednesday",
            "thursday": "thursday",
            "friday": "friday",
            "saturday": "saturday",
            "sunday": "sunday",
            "start_date": "start_date",
            "end_date": "end_date",
        },
        CalendarDate: {
            "calendar_id": "service_id",
            "date": "date",
            "exception_type": "exception_type",
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
        start_time = timer()

        self.logger.info("Reading data...")
        gtfs_feed = gtfs_kit.read_feed(url_or_filename, dist_units="km")

        if not skip_validation:
            self.logger.debug("Validating data...")
            results = gtfs_kit.validate(gtfs_feed, as_df=False)
            if results:
                self.logger.info("Validation errors:")
                self.logger.info(results)
                return

        with transaction.atomic():
            # TODO just some temporary feed handling to get things rolling
            feed, _ = Feed.objects.get_or_create(name=url_or_filename)

            self._delete_existing_gtfs_objects(feed)

            for model, gtfs_attribute in self.MODELS_AND_GTFS_KIT_ATTRIBUTES:
                self._import_model(feed, model, getattr(gtfs_feed, gtfs_attribute))

            # Update the feed's updated_at. We might want to do something else here.
            feed.save()

            self.logger.debug("Committing...")

        end_time = timer()
        self.logger.info(
            f'Successfully imported a GTFS feed from "{url_or_filename}" in {end_time - start_time:.2f} secs!'
        )

    def _delete_existing_gtfs_objects(self, feed):
        for model, _ in self.MODELS_AND_GTFS_KIT_ATTRIBUTES:
            self.logger.debug(f"Deleting existing {model._meta.verbose_name_plural}...")
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
        num_of_skipped = 0

        for num_of_processed, gtfs_row in enumerate(gtfs_data.itertuples(), 1):
            creation_attributes = {}

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
                model_field = model._meta.get_field(model_field_name)
                creation_attributes[model_field_name] = self._convert_value(
                    gtfs_value, model_field, gtfs_field
                )
            if model == CalendarDate and creation_attributes["calendar_id"] is None:
                # We don't support calendar dates without a calendar at least for now
                num_of_skipped += 1
            else:
                objs_to_create.append(
                    model(
                        feed_id=feed.id,
                        **creation_attributes,
                    )
                )

            if (
                num_of_processed % self.object_creation_batch_size == 0
                or num_of_processed >= num_of_rows  # yes this should never be GT
            ):
                created_objs = model.objects.bulk_create(objs_to_create)

                # update ID cache
                if "source_id" in creation_attributes:
                    self.id_cache[model].update(
                        {o.source_id: o.id for o in created_objs}
                    )

                objs_to_create = []

                self.logger.debug(
                    f"Processed {num_of_processed}/{num_of_rows} {plural_name}"
                )
                if num_of_processed >= num_of_rows and num_of_skipped:
                    self.logger.info(f"Skipped {num_of_skipped} {plural_name}")

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
                f"are {len(agency_ids)}) agencies in the feed."
            )
        return next(iter(agency_ids))

    @staticmethod
    def _convert_date(gtfs_date_str):
        return datetime.strptime(gtfs_date_str, "%Y%m%d").date()

    @staticmethod
    def _convert_time(gtfs_time_str):
        # TODO THIS DOES NOT ACTUALLY WORK IN ALL SITUATIONS!
        # In GTFS it is possible for a time to go past midnight like 26:00:00.
        # It is probably not possible to support those with Django's TimeField which we
        # are using ATM. For now the times that go too far are just clipped.
        hours, mins, secs = map(int, gtfs_time_str.split(":"))
        if hours > 23:
            hours = 23
            mins = 59
            secs = 59
        return time(hours, mins, secs)

    @staticmethod
    def _convert_point(gtfs_point):
        return Point(gtfs_point[1], gtfs_point[0])

    @staticmethod
    def _convert_int(gtfs_int):
        try:
            return int(gtfs_int)
        except ValueError:  # empty value Pandas nan
            return None
