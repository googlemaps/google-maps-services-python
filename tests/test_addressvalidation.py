# This Python file uses the following encoding: utf-8
#
# Copyright 2017 Google Inc. All rights reserved.
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

"""Tests for the addressvalidation module."""

import responses

import googlemaps
from . import TestCase


class AddressValidationTest(TestCase):
    def setUp(self):
        self.key = "AIzaSyD_sJl0qMA65CYHMBokVfMNA7AKyt5ERYs"
        self.client = googlemaps.Client(self.key)

    @responses.activate
    def test_simple_addressvalidation(self):
        responses.add(
            responses.POST,
            "https://addressvalidation.googleapis.com/v1:validateAddress",
            body='{"address": {"regionCode": "US","locality": "Mountain View","addressLines": "1600 Amphitheatre Pkwy"},"enableUspsCass":true}',
            status=200,
            content_type="application/json",
        )

        results = self.client.addressvalidation('1600 Amphitheatre Pk', regionCode='US', locality='Mountain View', enableUspsCass=True)

        self.assertEqual(1, len(responses.calls))
        self.assertURLEqual(
            "https://addressvalidation.googleapis.com/v1:validateAddress?" "key=%s" % self.key,
            responses.calls[0].request.url,
        )