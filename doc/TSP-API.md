# Transport Service Provider API Reference

THIS IS A DRAFT!

## Overview

This reference and recommendation is based on the GTFS static specification (January 17, 2019)

## Dataset files

TSP-API field requirements listed by dataset. For more information about the datasets or fields please see [GTFS static documentation](https://gtfs.org/reference/static)

### agency.txt

| Field Name        | Type          | Required                   | Description (in addition to GTFS spec)                                                                      |
| ----------------- | ------------- | -------------------------- | ----------------------------------------------------------------------------------------------------------- |
| `agency_id`       | ID            | **Conditionally Required** | Identifies a transit brand which is often synonymous with a transit agency.                                 |
| `agency_name`     | Text          | **Required**               | Full name of the transit agency.                                                                            |
| `agency_url`      | URL           | **Required**               | URL of the transit agency.                                                                                  |
| `agency_timezone` | Timezone      | **Required**               | `Europe/Helsinki` always to comply with the standard                                                        |
| `agency_lang`     | Language code | **Optional**               | Primary language used by this transit agency.                                                               |
| `agency_phone`    | Phone number  | **Optional**               | A voice telephone number for the specified agency.                                                          |
| `agency_fare_url` | URL           | **Optional**               | URL of a web page that allows a rider to purchase tickets or other fare instruments for that agency online. |
| `agency_email`    | Email         | **Optional**               | Email address actively monitored by the agency’s customer service department.                               |

### stops.txt

| Field Name | Type | Required | Description (in addition to GTFS spec) |
| ---------- | ---- | -------- | -------------------------------------- |
| `todo`     | TODO | **TODO** | TODO                                   |

TODO!
