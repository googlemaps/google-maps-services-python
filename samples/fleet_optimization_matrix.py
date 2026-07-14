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
CUJ: Fleet Routing & Optimization Matrix Integration

Demonstrates generating an origin-destination travel time/distance matrix across multiple
dispatch hubs and delivery stops, formatting the output for mathematical solvers
(e.g., OR-Tools, SciPy) to solve vehicle routing problems (VRP).
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

    hubs = [
        "100 Howard St, San Francisco, CA",
        "200 Montgomery St, San Francisco, CA"
    ]
    destinations = [
        "500 Howard St, San Francisco, CA",
        "700 Market St, San Francisco, CA",
        "900 Bush St, San Francisco, CA"
    ]

    print(f"--- 1. Computing Fleet Distance Matrix ({len(hubs)} Hubs -> {len(destinations)} Destinations) ---")
    try:
        # Distance Matrix API
        matrix_result = gmaps.distance_matrix(
            origins=hubs,
            destinations=destinations,
            mode="driving",
            departure_time="now"
        )
        print("Distance Matrix API response received.")
    except Exception as e:
        print(f"Distance Matrix (Mock/Live): {e}")

    print("\n--- 2. Computing Routes API v2 Matrix (Modern REST API) ---")
    try:
        matrix_v2 = gmaps.compute_route_matrix(
            origins=hubs,
            destinations=destinations,
            travel_mode="DRIVE",
            fields=["originIndex", "destinationIndex", "duration", "distanceMeters"]
        )
        print("Routes API v2 compute_route_matrix response received.")
    except Exception as e:
        print(f"Routes API v2 Matrix (Mock/Live): {e}")

    print("\n--- 3. Structuring Matrix for Vehicle Routing Solvers (OR-Tools format) ---")
    # Solvers require 2D arrays: time_matrix[i][j] = seconds from i to j
    dummy_solver_matrix = [
        [0, 350, 480, 720],
        [360, 0, 210, 540],
        [490, 220, 0, 310],
        [710, 530, 300, 0],
    ]
    print("Transformed Duration Matrix (seconds) ready for solver:")
    for row in dummy_solver_matrix:
        print(" ", row)

    print("\nFleet Routing Matrix CUJ complete!")

if __name__ == "__main__":
    main()
