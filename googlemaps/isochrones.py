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

"""Performs requests to the Google Maps Isochrones API."""

from googlemaps import exceptions

_ISOCHRONES_BASE_URL = "https://isochrones.googleapis.com"


def _isochrones_extract(response):
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


def _format_latlng(location):
    if isinstance(location, dict):
        if "latitude" in location:
            return {"latitude": location["latitude"], "longitude": location["longitude"]}
        elif "lat" in location:
            return {"latitude": location["lat"], "longitude": location["lng"]}
    elif isinstance(location, (tuple, list)):
        return {"latitude": location[0], "longitude": location[1]}
    elif isinstance(location, str) and "," in location:
        parts = [float(p.strip()) for p in location.split(",")]
        return {"latitude": parts[0], "longitude": parts[1]}
    raise ValueError("location must be a tuple (lat, lng), string 'lat,lng', or dict with latitude/longitude")


def generate_isochrones(
    client,
    location,
    travel_mode="DRIVE",
    travel_direction="FROM",
    duration_seconds=900,
    routing_preference=None,
):
    """Performs a request to the Google Maps Isochrones API to calculate area reachability.

    :param location: The origin location as a dict or lat/lng tuple.
    :type location: dict or tuple

    :param travel_mode: Mode of travel. Supported: "DRIVE", "WALK", "BICYCLE", "TRANSIT".
    :type travel_mode: string

    :param travel_direction: Direction of travel: "FROM" (outbound) or "TO" (inbound). Default "FROM".
    :type travel_direction: string

    :param duration_seconds: Travel duration limit in seconds (e.g. 900 for 15 min). Default 900.
    :type duration_seconds: int

    :param routing_preference: Routing preference ("TRAFFIC_AWARE" or "TRAFFIC_UNAWARE").
    :type routing_preference: string
    """
    params = {
        "location": _format_latlng(location),
        "travelMode": travel_mode,
        "travelDirection": travel_direction,
    }

    if duration_seconds is not None:
        params["travelDuration"] = "%ds" % duration_seconds

    if routing_preference:
        params["routingPreference"] = routing_preference

    return client._request(
        "/v1/isochrones:generate",
        {},
        base_url=_ISOCHRONES_BASE_URL,
        extract_body=_isochrones_extract,
        post_json=params,
    )
