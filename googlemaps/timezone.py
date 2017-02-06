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

from googlemaps import convert

from datetime import datetime


def timezone(client, location, timestamp=None, language=None):
    """Get time zone for a location on the earth, as well as that location's
    time offset from UTC.

    :param location: The latitude/longitude value representing the location to
        look up.
    :type location: string, dict, list, or tuple

    :param timestamp: Timestamp specifies the desired time as seconds since
        midnight, January 1, 1970 UTC. The Time Zone API uses the timestamp to
        determine whether or not Daylight Savings should be applied. Times
        before 1970 can be expressed as negative values. Optional. Defaults to
        ``datetime.utcnow()``.
    :type timestamp: int or datetime.datetime

    :param language: The language in which to return results.
    :type language: string

    :rtype: dict
    """

    params = {
        "location": convert.latlng(location),
        "timestamp": convert.time(timestamp or datetime.utcnow())
    }

    if language:
        params["language"] = language

    return client._request( "/maps/api/timezone/json", params)
