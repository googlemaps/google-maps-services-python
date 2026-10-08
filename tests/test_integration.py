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
Live Integration Tests for Google Maps Platform APIs.

These tests hit actual Google Maps Platform live servers.
They are executed when GOOGLE_MAPS_API_KEY or GMP_API_KEY environment variable is set.
Otherwise, they are automatically skipped.
"""

import os
import unittest
import googlemaps

API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY") or os.environ.get("GMP_API_KEY")


@unittest.skipIf(not API_KEY, "Integration tests require GOOGLE_MAPS_API_KEY environment variable")
class LiveApiIntegrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = googlemaps.Client(key=API_KEY)

    def test_places_search_devils_tower(self):
        """Test Places API (New) Text Search for 'Devils Tower'."""
        res = self.client.places_search_text(
            text_query="Devils Tower",
            fields=["places.id", "places.displayName", "places.formattedAddress", "places.location"]
        )

        self.assertIn("places", res)
        self.assertGreater(len(res["places"]), 0)

        first_result = res["places"][0]
        
        # Verify Name / Address contains 'Devils Tower'
        display_name = first_result.get("displayName", {}).get("text", "")
        formatted_address = first_result.get("formattedAddress", "")
        self.assertTrue(
            "Devils Tower" in display_name or "Devils Tower" in formatted_address,
            f"Expected 'Devils Tower' in result, got displayName='{display_name}', address='{formatted_address}'"
        )

        # Verify geographic location (Devils Tower, WY is approx 44.59° N, 104.71° W)
        loc = first_result.get("location", {})
        lat = loc.get("latitude", 0)
        lng = loc.get("longitude", 0)

        self.assertAlmostEqual(44.59, lat, delta=0.5)
        self.assertAlmostEqual(-104.71, lng, delta=0.5)

    def test_geocoding_and_reverse_geocoding(self):
        """Test live Geocoding and Reverse Geocoding APIs."""
        response = self.client.geocode("1600 Amphitheatre Pkwy, Mountain View, CA")
        results = response["results"] if isinstance(response, dict) else response
        self.assertGreater(len(results), 0)

        location = results[0]["geometry"]["location"]
        self.assertAlmostEqual(37.422, location["lat"], delta=0.05)
        self.assertAlmostEqual(-122.084, location["lng"], delta=0.05)

        rev_response = self.client.reverse_geocode((location["lat"], location["lng"]))
        rev_results = rev_response["results"] if isinstance(rev_response, dict) else rev_response
        self.assertGreater(len(rev_results), 0)
        self.assertIn("Mountain View", rev_results[0]["formatted_address"])

    def test_routes_v2_compute_routes(self):
        """Test live Routes API v2 compute_routes."""
        res = self.client.compute_routes(
            origin="San Francisco, CA",
            destination="San Jose, CA",
            travel_mode="DRIVE",
            fields=["routes.duration", "routes.distanceMeters", "routes.polyline.encodedPolyline"]
        )

        self.assertIn("routes", res)
        self.assertGreater(len(res["routes"]), 0)

        route = res["routes"][0]
        self.assertIn("distanceMeters", route)
        self.assertGreater(int(route["distanceMeters"]), 10000)  # > 10 km
        self.assertIn("polyline", route)

    def test_isochrones_api_live(self):
        """Test live Isochrones API generate_isochrones."""
        res = self.client.generate_isochrones(
            location=(37.7749, -122.4194),
            travel_mode="DRIVE",
            duration_seconds=900,
        )

        self.assertIn("isochrone", res)
        geo_json = res["isochrone"].get("geoJson", {})
        self.assertEqual("MultiPolygon", geo_json.get("type"))
        self.assertIn("coordinates", geo_json)
        self.assertGreater(len(geo_json["coordinates"]), 0)

    def test_solar_api_live(self):
        """Test live Solar API building insights."""
        res = self.client.find_closest_building_insights(
            location=(37.422, -122.084)
        )

        self.assertIn("solarPotential", res)

    def test_air_quality_api_live(self):
        """Test live Air Quality API current conditions."""
        res = self.client.air_quality_current_conditions(
            location=(37.422, -122.084)
        )

        self.assertIn("indexes", res)
        self.assertGreater(len(res["indexes"]), 0)

    def test_pollen_api_live(self):
        """Test live Pollen API forecast."""
        res = self.client.pollen_forecast(
            location=(37.422, -122.084),
            days=1
        )

        self.assertIn("dailyInfo", res)
        self.assertGreater(len(res["dailyInfo"]), 0)

    def test_elevation_mount_everest(self):
        """Test live Elevation API for Mount Everest."""
        everest_coords = (27.9881, 86.9250)
        res = self.client.elevation(locations=[everest_coords])

        self.assertEqual(len(res), 1)
        elevation_meters = res[0]["elevation"]
        self.assertGreater(elevation_meters, 8000)

    def test_address_validation_live(self):
        """Test live Address Validation API."""
        res = self.client.addressvalidation(
            addressLines=["1600 Amphitheatre Pk"],
            regionCode="US",
            locality="Mountain View"
        )

        self.assertIn("result", res)
        verdict = res["result"].get("verdict", {})
        self.assertTrue(len(verdict) > 0)
