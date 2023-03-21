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

"""Performs requests to the Google Maps Elevation API."""
from __future__ import annotations

from typing import TYPE_CHECKING, List, Union

from googlemaps import convert
from googlemaps.types import Location, DictStrAny

if TYPE_CHECKING:
    from googlemaps.client import Client


def elevation(client: Client, locations: List[Location]) -> List[DictStrAny]:
    """
    Provides elevation data for locations provided on the surface of the
    earth, including depth locations on the ocean floor (which return negative
    values)

    :param locations: List of latitude/longitude values from which you wish
        to calculate elevation data.
    :type locations: a single location, or a list of locations, where a
        location is a string, dict, list, or tuple

    :rtype: list of elevation data responses
    """
    params = {"locations": convert.shortest_path(locations)}
    return client._request("/maps/api/elevation/json", params).get("results", [])


def elevation_along_path(
    client: Client,
    path: Union[str, List[Location]],
    samples: int,
) -> List[DictStrAny]:
    """
    Provides elevation data sampled along a path on the surface of the earth.

    :param path: An encoded polyline string, or a list of latitude/longitude
        values from which you wish to calculate elevation data.
    :type path: string, dict, list, or tuple

    :param samples: The number of sample points along a path for which to
        return elevation data.
    :type samples: int

    :rtype: list of elevation data responses
    """

    if isinstance(path, str):
        path = "enc:%s" % path
    else:
        path = convert.shortest_path(path)

    params = {
        "path": path,
        "samples": samples
    }

    return client._request("/maps/api/elevation/json", params).get("results", [])
