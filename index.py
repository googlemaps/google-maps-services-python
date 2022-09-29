# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

## if your script calling addressvalidation is not is "googlemaps" folder
## adjust sys path to the "googlemaps" folder  
# import sys
# sys.path.insert(0, './google-maps-services-python-master')
import googlemaps
from concurrent.futures import ThreadPoolExecutor
    
# Development Test key [INTERNAL]
gmaps = googlemaps.Client(key='AIzaSyD_sJl0qMA65CYHMBokVfMNA7AKyt5ERYs')

### VALIDATE with Address Validation API

## THREADED requests
# Example 500 addresses
av_addresses = [
# Test 4 addresses
('New York', 'US', ''), ('Madrid', 'ES', ''), ('paris', 'FR', ''), ('Roma', 'IT', '')
]

## SINGLE request 
for x in av_addresses:
    addressvalidation_result = gmaps.addressvalidation(x[0], regionCode=x[1], locality=None)
    print(addressvalidation_result)

