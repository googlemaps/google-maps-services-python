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

"""Performs requests to the Google Maps Solar API."""

from googlemaps import convert
from googlemaps import exceptions

_SOLAR_BASE_URL = "https://solar.googleapis.com"


def _solar_extract(response):
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


def find_closest_building_insights(
    client, location, required_quality=None, exact_quality_required=False
):
    lat, lng = convert.normalize_lat_lng(location)
    params = {
        "location.latitude": convert.format_float(lat),
        "location.longitude": convert.format_float(lng),
    }
    if required_quality:
        params["requiredQuality"] = required_quality
    if exact_quality_required:
        params["exactQualityRequired"] = "true"

    return client._request(
        "/v1/buildingInsights:findClosest",
        params,
        base_url=_SOLAR_BASE_URL,
        extract_body=_solar_extract,
    )


def get_solar_data_layers(
    client,
    location,
    radius_meters,
    view=None,
    required_quality=None,
    exact_quality_required=False,
    pixel_size_meters=None,
):
    lat, lng = convert.normalize_lat_lng(location)
    params = {
        "location.latitude": convert.format_float(lat),
        "location.longitude": convert.format_float(lng),
        "radiusMeters": radius_meters,
    }
    if view:
        params["view"] = view
    if required_quality:
        params["requiredQuality"] = required_quality
    if exact_quality_required:
        params["exactQualityRequired"] = "true"
    if pixel_size_meters is not None:
        params["pixelSizeMeters"] = pixel_size_meters

    return client._request(
        "/v1/dataLayers:get",
        params,
        base_url=_SOLAR_BASE_URL,
        extract_body=_solar_extract,
    )
