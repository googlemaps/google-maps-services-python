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
CUJ 3: Travel & Local Discovery Assistant

Demonstrates using Places API (New / v1) for search autocompletion, text querying,
fetching rich place details, and retrieving place photo media.
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

    search_query = "ramen"
    user_typeahead = "Ram"
    print(f"--- 1. Place Autocomplete (New) for prefix '{user_typeahead}' ---")
    try:
        ac_res = gmaps.places_autocomplete_v1(input_text=user_typeahead, language_code="en")
        print("Autocomplete suggestions retrieved successfully.")
    except Exception as e:
        print(f"Places Autocomplete v1 (Mock/Live): {e}")

    print(f"\n--- 2. Text Search (New) for '{search_query}' in Tokyo ---")
    try:
        search_res = gmaps.places_search_text(
            text_query="ramen in Tokyo",
            fields=["places.id", "places.displayName", "places.formattedAddress", "places.rating", "places.photos"],
            open_now=True
        )
        print("Text Search v1 results retrieved successfully.")
    except Exception as e:
        print(f"Places Text Search v1 (Mock/Live): {e}")

    sample_place_id = "ChIJN1t_tDeuEmsRUsoyG83frY4"
    print(f"\n--- 3. Fetching Place Details (New) for Place ID '{sample_place_id}' ---")
    try:
        details_res = gmaps.place_v1(
            place_id=sample_place_id,
            fields=["id", "displayName", "formattedAddress", "websiteUri", "nationalPhoneNumber"]
        )
        print("Place Details v1 retrieved successfully.")
    except Exception as e:
        print(f"Place Details v1 (Mock/Live): {e}")

    sample_photo_resource = "places/ChIJN1t_tDeuEmsRUsoyG83frY4/photos/AXFsR3..."
    print(f"\n--- 4. Requesting Place Photo Media URL (New) ---")
    try:
        photo_res = gmaps.place_photo_v1(
            name=sample_photo_resource,
            max_width_px=800,
            skip_http_redirect=True
        )
        print("Place Photo media response retrieved successfully.")
    except Exception as e:
        print(f"Place Photo v1 (Mock/Live): {e}")

    print("\nTravel & Local Discovery CUJ complete!")

if __name__ == "__main__":
    main()
