# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Performs requests to the Places API (New / v1)."""

from googlemaps import convert
from googlemaps import exceptions

_PLACES_V1_BASE_URL = "https://places.googleapis.com"


def _places_v1_extract(response):
    if response.status_code != 200:
        try:
            body = response.json()
            if "error" in body:
                raise exceptions.ApiError(
                    body["error"].get("status", response.status_code),
                    body["error"].get("message"),
                )
        except ValueError:
            pass
        raise exceptions.HTTPError(response.status_code)
    return response.json()


def places_search_text(
    client,
    text_query,
    fields=None,
    included_type=None,
    location_bias=None,
    location_restriction=None,
    min_rating=None,
    open_now=None,
    price_levels=None,
    max_result_count=None,
    language_code=None,
    region_code=None,
):
    params = {"textQuery": text_query}

    if included_type:
        params["includedType"] = included_type
    if location_bias:
        params["locationBias"] = location_bias
    if location_restriction:
        params["locationRestriction"] = location_restriction
    if min_rating is not None:
        params["minRating"] = min_rating
    if open_now is not None:
        params["openNow"] = open_now
    if price_levels:
        params["priceLevels"] = convert.as_list(price_levels)
    if max_result_count is not None:
        params["maxResultCount"] = max_result_count
    if language_code:
        params["languageCode"] = language_code
    if region_code:
        params["regionCode"] = region_code

    headers = {}
    if fields:
        headers["X-Goog-FieldMask"] = convert.join_list(",", fields)

    return client._request(
        "/v1/places:searchText",
        {},
        base_url=_PLACES_V1_BASE_URL,
        extract_body=_places_v1_extract,
        post_json=params,
        requests_kwargs={"headers": headers} if headers else None,
    )


def places_search_nearby(
    client,
    location,
    radius,
    fields=None,
    included_types=None,
    excluded_types=None,
    max_result_count=None,
    language_code=None,
    region_code=None,
):
    lat, lng = convert.normalize_lat_lng(location)
    params = {
        "locationRestriction": {
            "circle": {
                "center": {
                    "latitude": lat,
                    "longitude": lng,
                },
                "radius": float(radius),
            }
        }
    }

    if included_types:
        params["includedTypes"] = convert.as_list(included_types)
    if excluded_types:
        params["excludedTypes"] = convert.as_list(excluded_types)
    if max_result_count is not None:
        params["maxResultCount"] = max_result_count
    if language_code:
        params["languageCode"] = language_code
    if region_code:
        params["regionCode"] = region_code

    headers = {}
    if fields:
        headers["X-Goog-FieldMask"] = convert.join_list(",", fields)

    return client._request(
        "/v1/places:searchNearby",
        {},
        base_url=_PLACES_V1_BASE_URL,
        extract_body=_places_v1_extract,
        post_json=params,
        requests_kwargs={"headers": headers} if headers else None,
    )


def place_v1(client, place_id, fields=None, language_code=None, region_code=None):
    if place_id.startswith("places/"):
        resource_name = place_id
    else:
        resource_name = "places/%s" % place_id

    params = {}
    if language_code:
        params["languageCode"] = language_code
    if region_code:
        params["regionCode"] = region_code

    headers = {}
    if fields:
        headers["X-Goog-FieldMask"] = convert.join_list(",", fields)

    return client._request(
        "/v1/%s" % resource_name,
        params,
        base_url=_PLACES_V1_BASE_URL,
        extract_body=_places_v1_extract,
        requests_kwargs={"headers": headers} if headers else None,
    )


def places_autocomplete_v1(
    client,
    input_text,
    location_bias=None,
    location_restriction=None,
    included_primary_types=None,
    included_region_codes=None,
    language_code=None,
    region_code=None,
    session_token=None,
    offset=None,
):
    params = {"input": input_text}

    if location_bias:
        params["locationBias"] = location_bias
    if location_restriction:
        params["locationRestriction"] = location_restriction
    if included_primary_types:
        params["includedPrimaryTypes"] = convert.as_list(included_primary_types)
    if included_region_codes:
        params["includedRegionCodes"] = convert.as_list(included_region_codes)
    if language_code:
        params["languageCode"] = language_code
    if region_code:
        params["regionCode"] = region_code
    if session_token:
        params["sessionToken"] = session_token
    if offset is not None:
        params["offset"] = offset

    return client._request(
        "/v1/places:autocomplete",
        {},
        base_url=_PLACES_V1_BASE_URL,
        extract_body=_places_v1_extract,
        post_json=params,
    )


def place_photo_v1(
    client,
    name,
    max_height_px=None,
    max_width_px=None,
    skip_http_redirect=False,
):
    if name.endswith("/media"):
        resource_name = name
    else:
        resource_name = "%s/media" % name

    if not resource_name.startswith("places/"):
        resource_name = "places/%s" % resource_name

    params = {}
    if max_height_px is not None:
        params["maxHeightPx"] = max_height_px
    if max_width_px is not None:
        params["maxWidthPx"] = max_width_px
    if skip_http_redirect:
        params["skipHttpRedirect"] = "true"

    return client._request(
        "/v1/%s" % resource_name,
        params,
        base_url=_PLACES_V1_BASE_URL,
        extract_body=_places_v1_extract,
    )
