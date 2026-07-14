#!/usr/bin/env python3
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
CUJ 1: Real Estate & Property Location Intelligence

Demonstrates validating a property address, resolving coordinates, discovering
nearby amenities (schools, parks), and fetching environmental insights (Air Quality,
Pollen levels, Solar potential).
"""

import os
import sys
import json
import googlemaps

def main():
    api_key = os.environ.get("GOOGLE_MAPS_API_KEY") or os.environ.get("GMP_API_KEY")
    if not api_key:
        print("[NOTICE] GOOGLE_MAPS_API_KEY environment variable not set.")
        print("Set it to run live requests: export GOOGLE_MAPS_API_KEY='your_key'")
        print("Running sample structure demo...\n")
        api_key = "AIzaDemoKeyForSampleExecution"

    gmaps = googlemaps.Client(key=api_key)

    address_to_evaluate = "1600 Amphitheatre Pkwy, Mountain View, CA"
    print(f"--- 1. Validating Property Address: '{address_to_evaluate}' ---")
    try:
        val_res = gmaps.addressvalidation(
            addressLines=["1600 Amphitheatre Pkwy"],
            regionCode="US",
            locality="Mountain View"
        )
        print("Address Validation Status:", val_res.get("result", {}).get("verdict", "Validated"))
    except Exception as e:
        print(f"Address Validation call (Mock/Live): {e}")

    print("\n--- 2. Geocoding Location Coordinates ---")
    try:
        geocode_res = gmaps.geocode(address_to_evaluate)
        if geocode_res:
            location = geocode_res[0]["geometry"]["location"]
            lat, lng = location["lat"], location["lng"]
            print(f"Coordinates: Lat {lat}, Lng {lng}")
        else:
            lat, lng = 37.4220, -122.0841
    except Exception as e:
        print(f"Geocoding fallback: {e}")
        lat, lng = 37.4220, -122.0841

    print(f"\n--- 3. Searching Nearby Amenities (Places API New) ---")
    try:
        places_res = gmaps.places_search_nearby(
            location=(lat, lng),
            radius=1000,
            included_types=["park", "school"],
            fields=["places.id", "places.displayName", "places.primaryType"]
        )
        print(f"Found nearby amenities: {len(places_res.get('places', []))} results")
    except Exception as e:
        print(f"Nearby Search (Mock/Live): {e}")

    print(f"\n--- 4. Fetching Environmental Intelligence ---")
    try:
        # Air Quality
        aq_res = gmaps.air_quality_current_conditions(location=(lat, lng))
        print("Air Quality response retrieved successfully.")
    except Exception as e:
        print(f"Air Quality (Mock/Live): {e}")

    try:
        # Pollen
        pollen_res = gmaps.pollen_forecast(location=(lat, lng), days=3)
        print("Pollen forecast retrieved successfully.")
    except Exception as e:
        print(f"Pollen Forecast (Mock/Live): {e}")

    try:
        # Solar Building Insights
        solar_res = gmaps.find_closest_building_insights(location=(lat, lng))
        print("Solar potential building insights retrieved successfully.")
    except Exception as e:
        print(f"Solar Insights (Mock/Live): {e}")

    print("\nReal Estate CUJ evaluation complete!")

if __name__ == "__main__":
    main()
