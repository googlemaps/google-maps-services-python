"""Performs requests to the Google Maps Directions API."""

from googlemaps import common
from googlemaps import convert


def directions(ctx, origin, destination,
               mode=None, waypoints=None, alternatives=False, avoid=None,
               language=None, units=None, region=None, departure_time=None,
               arrival_time=None):
    """Get directions between an origin point and a destination point.

    :param ctx: Shared googlemaps.Context
    :type ctx: googlemaps.Context

    :param origin: The address or latitude/longitude value from which you wish
            to calculate directions.
    :type origin: basestring or dict or tuple

    :param destination: The address or latitude/longitude value from which
        you wish to calculate directions.
    :type destination: basestring or dict or tuple

    :param mode: Specifies the mode of transport to use when calculating
        directions. One of "driving", "walking", "bicycling" or "transit"
    :type mode: basestring

    :param waypoints: Specifies an array of waypoints. Waypoints alter a
        route by routing it through the specified location(s).

    :param alternatives: If True, more than one route may be returned in the
        response.
    :type alternatives: bool

    :param avoid: Indicates that the calculated route(s) should avoid the
        indicated features.
    :type avoid: list or basestring

    :param language: The language in which to return results.
    :type language: basestring

    :param units: Specifies the unit system to use when displaying results.
        "metric" or "imperial"
    :type units: basestring

    :param region: The region code, specified as a ccTLD ("top-level domain"
        two-character value.
    :type region: basestring

    :param departure_time: Specifies the desired time of departure.
    :type departure_time: int or datetime.datetime

    :param arrival_time: Specifies the desired time of arrival for transit
        directions.
    :type arrival_time: int or datetime.datetime

    :rtype: list of routes
    """
    # TODO(mdr-eng): Add optimize_waypoints=True.

    params = {
        "origin": _convert_waypoint(origin),
        "destination": _convert_waypoint(destination)
    }

    if mode:
        if mode not in ["driving", "walking", "bicycling", "transit"]:
            raise Exception("Invalid travel mode.")
        params["mode"] = mode

    if waypoints:
        waypoints = convert.as_list(waypoints)
        waypoints = [_convert_waypoint(waypoint) for waypoint in waypoints]
        params["waypoints"] = convert.join_list("|", waypoints)

    if alternatives:
        params["alternatives"] = "true"

    if avoid:
        params["avoid"] = convert.join_list("|", avoid)

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

    return common._get(ctx, "/maps/api/directions/json", params)["routes"]

def _convert_waypoint(waypoint):
    if not isinstance(waypoint, basestring):
        return convert.latlng(waypoint)

    return waypoint
