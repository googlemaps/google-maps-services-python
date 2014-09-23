"""Performs requests to the Google Maps Directions API."""

from googlemaps import common
from googlemaps import convert

from datetime import datetime


def timezone(ctx, location, timestamp=datetime.now(), language=None):
    """Get time zone for a location on the earth, as well as that location's time offset from UTC.

    :param ctx: Shared googlemaps.Context
    :type ctx: googlemaps.Context

    :param location: The latitude/longitude value representing the location to look up.
    :type location: dict or tuple

    :param timestamp: Timestamp specifies the desired time as seconds since midnight, January 1, 
        1970 UTC. The Time Zone API uses the timestamp to determine whether or not Daylight Savings
        should be applied. Times before 1970 can be expressed as negative values. Optional.
    :type timestamp: int or datetime.datetime

    :param language: The language in which to return results.
    :type language: basestring

    :rtype: dict
    """

    if not isinstance(location, basestring):
        location = convert.latlng(location)

    timestamp = convert.time(timestamp)

    params = {
        "location": location,
        "timestamp": timestamp
    }

    if language:
        params["language"] = language

    return common._get(ctx, "/maps/api/timezone/json", params)
