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

"""Performs requests to the Google Maps Geocoding API."""
from googlemaps import common
from googlemaps import convert


def geocode(ctx, address=None, components=None, bounds=None, region=None,
            language=None):
    """
    Geocoding is the process of converting addresses
    (like "1600 Amphitheatre Parkway, Mountain View, CA") into geographic
    coordinates (like latitude 37.423021 and longitude -122.083739), which you
    can use to place markers or position the map.
    """

    params = {}

    if address:
        params["address"] = address

    if components:
        params["components"] = convert.components(components)

    if bounds:
        params["bounds"] = convert.bounds(bounds)

    if region:
        params["region"] = region

    if language:
        params["language"] = language

    return common._get(ctx, "/maps/api/geocode/json", params)["results"]


def reverse_geocode(ctx, latlng, result_type=None, location_type=None,
                    language=None):
    """
    Reverse geocoding is the process of converting geographic coordinates into a
    human-readable address.
    """
    # TODO(mdr-eng): Add ReST style doc comments.

    params = {
        "latlng": convert.latlng(latlng)
    }

    if result_type:
        params["result_type"] = convert.join_list("|", result_type)

    if location_type:
        params["location_type"] = convert.join_list("|", location_type)

    if language:
        params["language"] = language

    return common._get(ctx, "/maps/api/geocode/json", params)["results"]
