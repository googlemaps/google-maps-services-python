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

"""Performs requests to the Google Maps Directions API."""
from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional, Union, cast

from googlemaps import convert
from googlemaps.types import DictStrAny, Location, Timestamp, Unit, DirectionsMode, TransitMode, \
    TransitRoutingPreference, TrafficMode, DestinationAvoid

if TYPE_CHECKING:
    from googlemaps.client import Client


def directions(
    client: Client,
    origin: Location,
    destination: Location,
    mode: Optional[DirectionsMode] = None,
    waypoints: Optional[List[Location]] = None,
    alternatives: bool = False,
    avoid: Optional[Union[DestinationAvoid, List[DestinationAvoid]]] = None,
    language: Optional[str] = None,
    units: Optional[Unit] = None,
    region: Optional[str] = None,
    departure_time: Optional[Timestamp] = None,
    arrival_time: Optional[Timestamp] = None,
    optimize_waypoints: bool = False,
    transit_mode: Optional[TransitMode] = None,
    transit_routing_preference: Optional[TransitRoutingPreference] = None,
    traffic_model: Optional[TrafficMode] = None,
) -> List[DictStrAny]:
    """Get directions between an origin point and a destination point.

    :param origin: The address or latitude/longitude value from which you wish
        to calculate directions.
    :type origin: string, dict, list, or tuple

    :param destination: The address or latitude/longitude value from which
        you wish to calculate directions. You can use a place_id as destination
        by putting 'place_id:' as a prefix in the passing parameter.
    :type destination: string, dict, list, or tuple

    :param mode: Specifies the mode of transport to use when calculating
        directions. One of "driving", "walking", "bicycling" or "transit"
    :type mode: string

    :param waypoints: Specifies an array of waypoints. Waypoints alter a
        route by routing it through the specified location(s). To influence
        route without adding stop prefix the waypoint with `via`, similar to
        `waypoints = ["via:San Francisco", "via:Mountain View"]`.
    :type waypoints: a single location, or a list of locations, where a
        location is a string, dict, list, or tuple

    :param alternatives: If True, more than one route may be returned in the
        response.
    :type alternatives: bool

    :param avoid: Indicates that the calculated route(s) should avoid the
        indicated features.
    :type avoid: list or string

    :param language: The language in which to return results.
    :type language: string

    :param units: Specifies the unit system to use when displaying results.
        "metric" or "imperial"
    :type units: string

    :param region: The region code, specified as a ccTLD ("top-level domain"
        two-character value.
    :type region: string

    :param departure_time: Specifies the desired time of departure.
    :type departure_time: int or datetime.datetime

    :param arrival_time: Specifies the desired time of arrival for transit
        directions. Note: you can't specify both departure_time and
        arrival_time.
    :type arrival_time: int or datetime.datetime

    :param optimize_waypoints: Optimize the provided route by rearranging the
        waypoints in a more efficient order.
    :type optimize_waypoints: bool

    :param transit_mode: Specifies one or more preferred modes of transit.
        This parameter may only be specified for requests where the mode is
        transit. Valid values are "bus", "subway", "train", "tram", "rail".
        "rail" is equivalent to ["train", "tram", "subway"].
    :type transit_mode: string or list of strings

    :param transit_routing_preference: Specifies preferences for transit
        requests. Valid values are "less_walking" or "fewer_transfers"
    :type transit_routing_preference: string

    :param traffic_model: Specifies the predictive travel time model to use.
        Valid values are "best_guess" or "optimistic" or "pessimistic".
        The traffic_model parameter may only be specified for requests where
        the travel mode is driving, and where the request includes a
        departure_time.
    :type units: string

    :rtype: list of routes
    """

    params: DictStrAny = {
        "origin": convert.latlng(origin),
        "destination": convert.latlng(destination)
    }

    if mode:
        # NOTE(broady): the mode parameter is not validated by the Maps API
        # server. Check here to prevent silent failures.
        if mode not in ["driving", "walking", "bicycling", "transit"]:
            raise ValueError("Invalid travel mode.")
        params["mode"] = mode

    if waypoints:
        waypoints_val = convert.location_list(waypoints)
        if optimize_waypoints:
            waypoints_val = "optimize:true|" + waypoints_val
        params["waypoints"] = waypoints_val

    if alternatives:
        params["alternatives"] = "true"

    if avoid:
        params["avoid"] = convert.join_list("|", cast(Union[str, List[str]], avoid))

    if language:
        params["language"] = language

    if units:
        params["units"] = units

    if region:
        params["region"] = region

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

    return client._request("/maps/api/directions/json", params).get("routes", [])
