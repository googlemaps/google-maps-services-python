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
                    departure_time=None, arrival_time=None, transit_mode=None,
                    transit_routing_preference=None, traffic_model=None):
    """ Gets travel distance and time for a matrix of origins and destinations.

    :param origins: One or more locations and/or latitude/longitude values,
        from which to calculate distance and time. If you pass an address as
        a string, the service will geocode the string and convert it to a
        latitude/longitude coordinate to calculate directions.
    :type origins: a single location, or a list of locations, where a
        location is a string, dict, list, or tuple

    :param destinations: One or more addresses and/or lat/lng values, to
        which to calculate distance and time. If you pass an address as a
        string, the service will geocode the string and convert it to a
        latitude/longitude coordinate to calculate directions.
    :type destinations: a single location, or a list of locations, where a
        location is a string, dict, list, or tuple

    :param mode: Specifies the mode of transport to use when calculating
        directions. Valid values are "driving", "walking", "transit" or
        "bicycling".
    :type mode: string

    :param language: The language in which to return results.
    :type language: string

    :param avoid: Indicates that the calculated route(s) should avoid the
        indicated features. Valid values are "tolls", "highways" or "ferries".
    :type avoid: string

    :param units: Specifies the unit system to use when displaying results.
        Valid values are "metric" or "imperial".
    :type units: string

    :param departure_time: Specifies the desired time of departure.
    :type departure_time: int or datetime.datetime

    :param arrival_time: Specifies the desired time of arrival for transit
        directions. Note: you can't specify both departure_time and
        arrival_time.
    :type arrival_time: int or datetime.datetime

    :param transit_mode: Specifies one or more preferred modes of transit.
        This parameter may only be specified for requests where the mode is
        transit. Valid values are "bus", "subway", "train", "tram", "rail".
        "rail" is equivalent to ["train", "tram", "subway"].
    :type transit_mode: string or list of strings

    :param transit_routing_preference: Specifies preferences for transit
        requests. Valid values are "less_walking" or "fewer_transfers".
    :type transit_routing_preference: string

    :param traffic_model: Specifies the predictive travel time model to use.
        Valid values are "best_guess" or "optimistic" or "pessimistic".
        The traffic_model parameter may only be specified for requests where
        the travel mode is driving, and where the request includes a
        departure_time.

    :rtype: matrix of distances. Results are returned in rows, each row
        containing one origin paired with each destination.
    """

    params = {
        "origins": convert.location_list(origins),
        "destinations": convert.location_list(destinations)
    }

    if mode:
        # NOTE(broady): the mode parameter is not validated by the Maps API
        # server. Check here to prevent silent failures.
        if mode not in ["driving", "walking", "bicycling", "transit"]:
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

    if arrival_time:
        params["arrival_time"] = convert.time(arrival_time)

    if departure_time and arrival_time:
        raise ValueError("Should not specify both departure_time and"
                         "arrival_time.")

    if transit_mode:
        params["transit_mode"] = convert.join_list("|", transit_mode)

    if transit_routing_preference:
        params["transit_routing_preference"] = transit_routing_preference

    if traffic_model:
        params["traffic_model"] = traffic_model

    return client._request("/maps/api/distancematrix/json", params)
