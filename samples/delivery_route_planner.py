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
CUJ 2: Delivery & Logistics Route Planning

Demonstrates using Routes API v2 (compute_route_matrix and compute_routes)
to estimate distances/ETAs across multiple delivery drop-off locations and compute
turn-by-turn driving directions.
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

    depot = "San Francisco Ferry Building, San Francisco, CA"
    deliveries = [
        "Fisherman's Wharf, San Francisco, CA",
        "Union Square, San Francisco, CA",
        "Golden Gate Park, San Francisco, CA",
    ]

    print(f"--- 1. Computing Route Distance/ETA Matrix (Depot -> {len(deliveries)} Stop Locations) ---")
    try:
        matrix = gmaps.compute_route_matrix(
            origins=[depot],
            destinations=deliveries,
            travel_mode="DRIVE",
            fields=["originIndex", "destinationIndex", "duration", "distanceMeters", "status"]
        )
        print("Distance Matrix response received successfully.")
    except Exception as e:
        print(f"Compute Route Matrix (Mock/Live): {e}")

    print("\n--- 2. Computing Primary Delivery Route Polyline and Directions ---")
    try:
        route_res = gmaps.compute_routes(
            origin=depot,
            destination=deliveries[-1],
            fields=["routes.duration", "routes.distanceMeters", "routes.polyline.encodedPolyline"]
        )
        print("Routes v2 compute_routes response received successfully.")
    except Exception as e:
        print(f"Compute Routes (Mock/Live): {e}")

    print("\nDelivery Route Planning CUJ complete!")

if __name__ == "__main__":
    main()
