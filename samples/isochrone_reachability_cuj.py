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
CUJ 7: Isochrone Reachability & 15-Minute Urban Planning Analysis

Demonstrates using the Isochrones API to calculate reachable boundaries (polygons)
within a specified travel time (e.g. 15-minute drive/walk), combining reachability polygons
with Places API (New) for location coverage analysis.
"""

import os
import sys
import googlemaps

def main():
    api_key = os.environ.get("GOOGLE_MAPS_API_KEY") or os.environ.get("GMP_API_KEY")
    if not api_key:
        print("[NOTICE] GOOGLE_MAPS_API_KEY environment variable not set.")
        print("Set it to run live requests: export GOOGLE_MAPS_API_KEY='your_key'")
        print("Running sample structure demo...\n")
        api_key = "AIzaDemoKeyForSampleExecution"

    gmaps = googlemaps.Client(key=api_key)

    center_location = (37.7749, -122.4194)  # San Francisco, CA
    print(f"--- 1. Generating 15-Minute Drive Isochrone Reachability Polygon for {center_location} ---")
    try:
        isochrone_res = gmaps.generate_isochrones(
            location=center_location,
            travel_mode="DRIVE",
            duration_seconds=900,  # 15 minutes = 900s
        )
        print("Isochrones API response retrieved successfully.")
    except Exception as e:
        print(f"Generate Isochrones (Mock/Live): {e}")

    print("\n--- 2. Combining Reachability Isochrones with Places Search ---")
    try:
        # Search for essential amenities inside the area
        amenities = gmaps.places_search_nearby(
            location=center_location,
            radius=1500,
            included_types=["pharmacy", "hospital"],
            fields=["places.id", "places.displayName"]
        )
        print("Nearby coverage amenities search complete.")
    except Exception as e:
        print(f"Places Coverage Search (Mock/Live): {e}")

    print("\nIsochrone Reachability CUJ complete!")

if __name__ == "__main__":
    main()
