#
# Copyright 2015 Google Inc. All rights reserved.
#
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
#

"""Performs requests to the Google Maps Roads API."""

import googlemaps
from googlemaps import convert


_ROADS_BASE_URL = "https://roads.googleapis.com"


def snap_to_roads(client, path, interpolate=False):
    """Snaps a path to the most likely roads travelled.

    Takes up to 100 GPS points collected along a route, and returns a similar
    set of data with the points snapped to the most likely roads the vehicle
    was traveling along.

    :param path: The path to be snapped.
    :type path: a single location, or a list of locations, where a
        location is a string, dict, list, or tuple

    :param interpolate: Whether to interpolate a path to include all points
        forming the full road-geometry. When true, additional interpolated
        points will also be returned, resulting in a path that smoothly follows
        the geometry of the road, even around corners and through tunnels.
        Interpolated paths may contain more points than the original path.
    :type interpolate: bool

    :rtype: A list of snapped points.
    """

    params = {"path": convert.location_list(path)}

    if interpolate:
        params["interpolate"] = "true"

    return client._request("/v1/snapToRoads", params,
                       base_url=_ROADS_BASE_URL,
                       accepts_clientid=False,
                       extract_body=_roads_extract).get("snappedPoints", [])

def nearest_roads(client, points):
    """Find the closest road segments for each point

    Takes up to 100 independent coordinates, and returns the closest road
    segment for each point. The points passed do not need to be part of a
    continuous path.

    :param points: The points for which the nearest road segments are to be
        located.
    :type points: a single location, or a list of locations, where a
        location is a string, dict, list, or tuple

    :rtype: A list of snapped points.
    """

    params = {"points": convert.location_list(points)}

    return client._request("/v1/nearestRoads", params,
                       base_url=_ROADS_BASE_URL,
                       accepts_clientid=False,
                       extract_body=_roads_extract).get("snappedPoints", [])

def speed_limits(client, place_ids):
    """Returns the posted speed limit (in km/h) for given road segments.

    :param place_ids: The Place ID of the road segment. Place IDs are returned
        by the snap_to_roads function. You can pass up to 100 Place IDs.
    :type place_ids: str or list

    :rtype: list of speed limits.
    """

    params = [("placeId", place_id) for place_id in convert.as_list(place_ids)]

    return client._request("/v1/speedLimits", params,
                       base_url=_ROADS_BASE_URL,
                       accepts_clientid=False,
                       extract_body=_roads_extract).get("speedLimits", [])


def snapped_speed_limits(client, path):
    """Returns the posted speed limit (in km/h) for given road segments.

    The provided points will first be snapped to the most likely roads the
    vehicle was traveling along.

    :param path: The path of points to be snapped.
    :type path: a single location, or a list of locations, where a
        location is a string, dict, list, or tuple

    :rtype: dict with a list of speed limits and a list of the snapped points.
    """

    params = {"path": convert.location_list(path)}

    return client._request("/v1/speedLimits", params,
                       base_url=_ROADS_BASE_URL,
                       accepts_clientid=False,
                       extract_body=_roads_extract)


def _roads_extract(resp):
    """Extracts a result from a Roads API HTTP response."""

    try:
        j = resp.json()
    except:
        if resp.status_code != 200:
            raise googlemaps.exceptions.HTTPError(resp.status_code)

        raise googlemaps.exceptions.ApiError("UNKNOWN_ERROR",
                                             "Received a malformed response.")

    if "error" in j:
        error = j["error"]
        status = error["status"]

        if status == "RESOURCE_EXHAUSTED":
            raise googlemaps.exceptions._OverQueryLimit(status,
                                                        error.get("message"))

        raise googlemaps.exceptions.ApiError(status, error.get("message"))

    if resp.status_code != 200:
        raise googlemaps.exceptions.HTTPError(resp.status_code)

    return j
