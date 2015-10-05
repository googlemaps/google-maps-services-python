# This Python file uses the following encoding: utf-8
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

"""Tests for the timezone module."""

import responses
import mock
import datetime

import googlemaps
import test as _test


class TimezoneTest(_test.TestCase):

    def setUp(self):
        self.key = "AIzaasdf"
        self.client = googlemaps.Client(self.key)

    @responses.activate
    def test_los_angeles(self):
        responses.add(responses.GET,
                      "https://maps.googleapis.com/maps/api/timezone/json",
                      body='{"status":"OK"}',
                      status=200,
                      content_type="application/json")

        ts = 1331766000
        timezone = self.client.timezone((39.603481, -119.682251), ts)
        self.assertIsNotNone(timezone)

        self.assertEqual(1, len(responses.calls))
        self.assertURLEqual("https://maps.googleapis.com/maps/api/timezone/json"
                            "?location=39.603481,-119.682251&timestamp=%d"
                            "&key=%s" %
                            (ts, self.key),
                            responses.calls[0].request.url)

    class MockDatetime(object):

        def now(self):
            return datetime.datetime.fromtimestamp(1608)
        utcnow = now

    @responses.activate
    @mock.patch("googlemaps.timezone.datetime", MockDatetime())
    def test_los_angeles_with_no_timestamp(self):
        responses.add(responses.GET,
                      "https://maps.googleapis.com/maps/api/timezone/json",
                      body='{"status":"OK"}',
                      status=200,
                      content_type="application/json")

        timezone = self.client.timezone((39.603481, -119.682251))
        self.assertIsNotNone(timezone)

        self.assertEqual(1, len(responses.calls))
        self.assertURLEqual("https://maps.googleapis.com/maps/api/timezone/json"
                            "?location=39.603481,-119.682251&timestamp=%d"
                            "&key=%s" %
                            (1608, self.key),
                            responses.calls[0].request.url)
