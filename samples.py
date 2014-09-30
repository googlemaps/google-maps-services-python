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

"""Samples demonstrating the googlemaps package."""
# TODO(mdr-eng): clean up and replace with tests/move to README file.

import googlemaps

def main():
    c = googlemaps.Context(
            key="AIzaSyDyZdCabN8GKh786tdj16gq80xalbbfqDM",
            timeout=5)

    locations = [(40.714728, -73.998672), (-34.397, 150.644)]
    print googlemaps.elevation(c, locations)
    print googlemaps.elevation(c, (40.714728, -73.998672))

    print googlemaps.elevation_along_path(c, locations, 3)

    geocoded = googlemaps.geocode(c, "48 Pirrama Rd")

    print geocoded

    print googlemaps.reverse_geocode(c, geocoded[0]["geometry"]["location"])

    print googlemaps.reverse_geocode(c,
            latlng=(-33.86536501970851,151.1969187802915),
            result_type=["country", "political"])

    print googlemaps.geocode(c, components={"country": "US"})

    print googlemaps.directions(c,
            "Sydney",
            "Melbourne",
            alternatives=True
    )

if __name__ == '__main__':
    main()
