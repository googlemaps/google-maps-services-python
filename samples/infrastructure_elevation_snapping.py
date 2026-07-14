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
CUJ: Infrastructure & Environmental Analysis (GPS Road Snapping & Elevation)

Demonstrates snapping noisy GPS breadcrumbs back onto road geometries (Roads API)
and querying topographical elevation profiles along coordinate paths (Elevation API).
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

    # Simulated noisy GPS breadcrumbs from a moving vehicle
    raw_gps_points = [
        (60.170880, 24.942700),
        (60.170879, 24.942712),
        (60.170877, 24.942724),
    ]

    print("--- 1. Snapping Noisy GPS Breadcrumbs to Roads (Roads API) ---")
    try:
        snapped = gmaps.snap_to_roads(path=raw_gps_points, interpolate=True)
        print("Snap to Roads API response received.")
    except Exception as e:
        print(f"Snap to Roads (Mock/Live): {e}")

    print("\n--- 2. Querying Elevation Data Profiles (Elevation API) ---")
    try:
        # Sample elevation for coordinate locations
        elevation_data = gmaps.elevation(locations=raw_gps_points)
        print("Elevation API response received.")

        # Sample elevation sampled continuously along a path
        path_elevation = gmaps.elevation_along_path(path=raw_gps_points, samples=5)
        print("Elevation Along Path API response received.")
    except Exception as e:
        print(f"Elevation API (Mock/Live): {e}")

    print("\nInfrastructure & Environmental Analysis CUJ complete!")

if __name__ == "__main__":
    main()
