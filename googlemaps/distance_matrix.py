#
# Copyright 2014 Google Inc. All rights reserved.
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

"""Performs requests to the Google Maps Distance Matrix API."""

from googlemaps import convert
from googlemaps.convert import as_list

def distance_matrix(client, origins, destinations,
                    mode=None, language=None, avoid=None, units=None,
                    departure_time=None):
    """ Gets travel distance and time for a matrix of origins and destinations.

    :param origins: One or more addresses and/or latitude/longitude values,
            from which to calculate distance and time. If you pass an address
            as a string, the service will geocode the string and convert it to
            a latitude/longitude coordinate to calculate directions.
    :type origins: list of strings, dicts or tuples

    :param destinations: One or more addresses and/or lat/lng values, to
            which to calculate distance and time. If you pass an address as a
            string, the service will geocode the string and convert it to a
            latitude/longitude coordinate to calculate directions.
    :type destinations: list of strings, dicts or tuples

    :param mode: Specifies the mode of transport to use when calculating
            directions. Valid values are "driving", "walking" or "bicycling".
    :type mode: string

    :param language: The language in which to return results.
    :type language: string

    :param avoid: Indicates that the calculated route(s) should avoid the
        indicated features. Valid values are "tolls", "highways" or "ferries"
    :type avoid: string

    :param units: Specifies the unit system to use when displaying results.
        Valid values are "metric" or "imperial"
    :type units: string

    :param departure_time: Specifies the desired time of departure as seconds
        since midnight, January 1, 1970 UTC. The departure time may be
        specified by Google Maps API for Work customers to receive trip
        duration considering current traffic conditions. The departure_time
        must be set to within a few minutes of the current time.
    :type departure_time: int or datetime.datetime

    :rtype: matrix of distances. Results are returned in rows, each row
        containing one origin paired with each destination.
    """

    params = {
        "origins": _convert_path(origins),
        "destinations": _convert_path(destinations)
    }

    if mode:
        if mode not in ["driving", "walking", "bicycling"]:
            raise ValueError("Invalid travel mode.")
        params["mode"] = mode

    if language:
        params["language"] = language

    if avoid:
        if avoid not in ["tolls", "highways", "ferries"]:
            raise ValueError("Invalid route restriction.")
        params["avoid"] = avoid

    if units:
        params["units"] = units

    if departure_time:
        params["departure_time"] = convert.time(departure_time)

    return client._get("/maps/api/distancematrix/json", params)


def _convert_path(waypoints):
    # Handle the single-tuple case
    if type(waypoints) is tuple:
        waypoints = [waypoints]
    else:
        waypoints = as_list(waypoints)

    return convert.join_list("|",
            [(k if convert.is_string(k) else convert.latlng(k))
                for k in waypoints])
