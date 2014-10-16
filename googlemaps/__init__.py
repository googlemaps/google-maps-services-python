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

from googlemaps.common import ApiError
from googlemaps.common import Context
from googlemaps.directions import directions
from googlemaps.distance_matrix import distance_matrix
from googlemaps.elevation import elevation
from googlemaps.elevation import elevation_along_path
from googlemaps.geocoding import geocode
from googlemaps.geocoding import reverse_geocode
from googlemaps.timezone import timezone

# Allow sphinx to pick up these symbols for the documentation.
__all__ = ['Context', 'ApiError', 'geocode', 'reverse_geocode',
           'directions', 'distance_matrix', 'elevation',
           'elevation_along_path', 'timezone']
