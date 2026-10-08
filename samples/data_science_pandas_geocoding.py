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
CUJ: Data Pipeline Integration (Batch Geocoding & Pandas Export)

Demonstrates how to process raw address streams, validate deliverability, geocode
them into precise coordinates, and construct structured datasets suitable for Pandas
or GeoPandas spatial analysis.
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

    raw_addresses = [
        "1600 Amphitheatre Pkwy, Mountain View, CA",
        "1 Wall St, New York, NY",
        "500 5th Ave, Seattle, WA",
    ]

    print("--- 1. Batch Geocoding Raw Address Stream ---")
    dataset = []

    for addr in raw_addresses:
        try:
            results = gmaps.geocode(addr)
            if results:
                geo = results[0]["geometry"]["location"]
                fmt_addr = results[0].get("formatted_address", addr)
                place_id = results[0].get("place_id", "")
                record = {
                    "original_input": addr,
                    "formatted_address": fmt_addr,
                    "latitude": geo["lat"],
                    "longitude": geo["lng"],
                    "place_id": place_id,
                }
            else:
                record = {"original_input": addr, "error": "No results"}
        except Exception as e:
            record = {"original_input": addr, "error": str(e)}

        dataset.append(record)
        print(f"Processed: {addr} -> Lat/Lng: ({record.get('latitude')}, {record.get('longitude')})")

    print("\n--- 2. Exporting to Tabular Structure (Pandas DataFrame Compatible) ---")
    try:
        import pandas as pd
        df = pd.DataFrame(dataset)
        print("\nPandas DataFrame Output:")
        print(df.to_string())
    except ImportError:
        print("Pandas not installed in environment. Standard Python record representations:")
        for r in dataset:
            print(" ", r)

    print("\nBatch Geocoding & Data Pipeline CUJ complete!")

if __name__ == "__main__":
    main()
