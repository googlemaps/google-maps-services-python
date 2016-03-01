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

"""Tests for the elevation module."""

import datetime
import responses

import googlemaps
import test as _test

class ElevationTest(_test.TestCase):

    def setUp(self):
        self.key = 'AIzaasdf'
        self.client = googlemaps.Client(self.key)

    @responses.activate
    def test_elevation_single(self):
        responses.add(responses.GET,
                      'https://maps.googleapis.com/maps/api/elevation/json',
                      body='{"status":"OK","results":[]}',
                      status=200,
                      content_type='application/json')

        results = self.client.elevation((40.714728, -73.998672))

        self.assertEqual(1, len(responses.calls))
        self.assertURLEqual('https://maps.googleapis.com/maps/api/elevation/json?'
                            'locations=enc:abowFtzsbM&key=%s' % self.key,
                            responses.calls[0].request.url)

    @responses.activate
    def test_elevation_single_list(self):
        responses.add(responses.GET,
                      'https://maps.googleapis.com/maps/api/elevation/json',
                      body='{"status":"OK","results":[]}',
                      status=200,
                      content_type='application/json')

        results = self.client.elevation([(40.714728, -73.998672)])

        self.assertEqual(1, len(responses.calls))
        self.assertURLEqual('https://maps.googleapis.com/maps/api/elevation/json?'
                            'locations=enc:abowFtzsbM&key=%s' % self.key,
                            responses.calls[0].request.url)

    @responses.activate
    def test_elevation_multiple(self):
        responses.add(responses.GET,
                      'https://maps.googleapis.com/maps/api/elevation/json',
                      body='{"status":"OK","results":[]}',
                      status=200,
                      content_type='application/json')

        locations = [(40.714728, -73.998672), (-34.397, 150.644)]
        results = self.client.elevation(locations)

        self.assertEqual(1, len(responses.calls))
        self.assertURLEqual('https://maps.googleapis.com/maps/api/elevation/json?'
                            'locations=enc:abowFtzsbMhgmiMuobzi@&key=%s' % self.key,
                            responses.calls[0].request.url)

    def test_elevation_along_path_single(self):
        with self.assertRaises(googlemaps.exceptions.ApiError):
            results = self.client.elevation_along_path(
                    [(40.714728, -73.998672)], 5)

    @responses.activate
    def test_elevation_along_path(self):
        responses.add(responses.GET,
                      'https://maps.googleapis.com/maps/api/elevation/json',
                      body='{"status":"OK","results":[]}',
                      status=200,
                      content_type='application/json')

        path = [(40.714728, -73.998672), (-34.397, 150.644)]

        results = self.client.elevation_along_path(path, 5)

        self.assertEqual(1, len(responses.calls))
        self.assertURLEqual('https://maps.googleapis.com/maps/api/elevation/json?'
                            'path=enc:abowFtzsbMhgmiMuobzi@&'
                            'key=%s&samples=5' % self.key,
                            responses.calls[0].request.url)

    @responses.activate
    def test_short_latlng(self):
        responses.add(responses.GET,
                      'https://maps.googleapis.com/maps/api/elevation/json',
                      body='{"status":"OK","results":[]}',
                      status=200,
                      content_type='application/json')

        results = self.client.elevation((40, -73))

        self.assertEqual(1, len(responses.calls))
        self.assertURLEqual('https://maps.googleapis.com/maps/api/elevation/json?'
                            'locations=40,-73&key=%s' % self.key,
                            responses.calls[0].request.url)
