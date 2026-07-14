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

"""Performs requests to the Google Maps Air Quality API."""

from googlemaps import convert
from googlemaps import exceptions

_AIRQUALITY_BASE_URL = "https://airquality.googleapis.com"


def _airquality_extract(response):
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


def air_quality_current_conditions(
    client,
    location,
    extra_computations=None,
    language_code=None,
    uaqi_color_palette=None,
):
    lat, lng = convert.normalize_lat_lng(location)
    params = {
        "location": {
            "latitude": lat,
            "longitude": lng,
        }
    }

    if extra_computations:
        params["extraComputations"] = convert.as_list(extra_computations)
    if language_code:
        params["languageCode"] = language_code
    if uaqi_color_palette:
        params["uaqiColorPalette"] = uaqi_color_palette

    return client._request(
        "/v1/currentConditions:lookup",
        {},
        base_url=_AIRQUALITY_BASE_URL,
        extract_body=_airquality_extract,
        post_json=params,
    )
