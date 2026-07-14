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

"""Performs requests to the Google Maps Routes API."""

from googlemaps import convert
from googlemaps import exceptions

_ROUTES_BASE_URL = "https://routes.googleapis.com"


def _routes_extract(response):
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


def route_waypoint(arg):
    if isinstance(arg, dict) and (
        "location" in arg or "placeId" in arg or "address" in arg
    ):
        return arg

    if convert.is_string(arg):
        if arg.startswith("place_id:"):
            return {"placeId": arg[len("place_id:") :]}
        else:
            return {"address": arg}

    try:
        lat, lng = convert.normalize_lat_lng(arg)
        return {"location": {"latLng": {"latitude": lat, "longitude": lng}}}
    except Exception:
        raise ValueError("Invalid waypoint: %s" % arg)


def compute_routes(client, origin, destination, fields=None, travel_mode=None):
    params = {
        "origin": route_waypoint(origin),
        "destination": route_waypoint(destination),
    }

    if travel_mode:
        params["travelMode"] = travel_mode

    headers = {}
    if fields:
        headers["X-Goog-FieldMask"] = convert.join_list(",", fields)

    return client._request(
        "/directions/v2:computeRoutes",
        {},  # GET params are empty
        base_url=_ROUTES_BASE_URL,
        extract_body=_routes_extract,
        post_json=params,
        requests_kwargs={"headers": headers} if headers else None,
    )


def compute_route_matrix(
    client, origins, destinations, fields=None, travel_mode=None, routing_preference=None
):
    if not origins or not destinations:
        raise ValueError("Must specify both origins and destinations.")

    origin_list = [{"waypoint": route_waypoint(o)} for o in convert.as_list(origins)]
    destination_list = [
        {"waypoint": route_waypoint(d)} for d in convert.as_list(destinations)
    ]

    params = {
        "origins": origin_list,
        "destinations": destination_list,
    }

    if travel_mode:
        params["travelMode"] = travel_mode
    if routing_preference:
        params["routingPreference"] = routing_preference

    headers = {}
    if fields:
        headers["X-Goog-FieldMask"] = convert.join_list(",", fields)

    return client._request(
        "/distanceMatrix/v2:computeRouteMatrix",
        {},
        base_url=_ROUTES_BASE_URL,
        extract_body=_routes_extract,
        post_json=params,
        requests_kwargs={"headers": headers} if headers else None,
    )
