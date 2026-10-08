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

"""Performs requests to the Google Maps Pollen API."""

from googlemaps import convert
from googlemaps import exceptions

_POLLEN_BASE_URL = "https://pollen.googleapis.com"


def _pollen_extract(response):
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


def pollen_forecast(
    client,
    location,
    days=1,
    language_code=None,
    plants_description=None,
):
    lat, lng = convert.normalize_lat_lng(location)
    params = {
        "location.latitude": convert.format_float(lat),
        "location.longitude": convert.format_float(lng),
        "days": days,
    }

    if language_code:
        params["languageCode"] = language_code
    if plants_description is not None:
        params["plantsDescription"] = "true" if plants_description else "false"

    return client._request(
        "/v1/forecast:lookup",
        params,
        base_url=_POLLEN_BASE_URL,
        extract_body=_pollen_extract,
    )
