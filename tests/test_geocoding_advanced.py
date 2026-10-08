#
# Copyright 2024 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#

"""Advanced / regression tests for the geocoding module.

These tests are specifically aimed at issue #540 ("unexpected keyword argument
``enable_address_descriptor``"). They exhaustively pin down the public
signature of :func:`googlemaps.Client.reverse_geocode` and the on-the-wire
behaviour of the ``enable_address_descriptor`` flag so the regression cannot
silently come back in a future release.
"""

import inspect
from urllib.parse import parse_qs, urlparse

import responses

import googlemaps
from googlemaps import geocoding

from . import TestCase


_GEOCODE_URL = "https://maps.googleapis.com/maps/api/geocode/json"

_DESCRIPTOR_BODY = (
    '{"status":"OK","results":[],'
    '"address_descriptor":{'
    '"landmarks":[{"placeId":"id","display_name":{"text":"Opera House"}}],'
    '"areas":[{"placeId":"area1","display_name":{"text":"Sydney"}}]'
    '}}'
)
_PLAIN_BODY = '{"status":"OK","results":[]}'


def _query(call):
    """Return the parsed query string for a captured ``responses`` call."""
    return parse_qs(urlparse(call.request.url).query)


class ReverseGeocodeSignatureTest(TestCase):
    """Pin the public signature so issue #540 cannot regress."""

    def test_module_function_accepts_enable_address_descriptor(self):
        sig = inspect.signature(geocoding.reverse_geocode)
        self.assertIn("enable_address_descriptor", sig.parameters)
        self.assertFalse(
            sig.parameters["enable_address_descriptor"].default,
            "enable_address_descriptor must default to a falsy value",
        )

    def test_client_method_accepts_enable_address_descriptor(self):
        client = googlemaps.Client(key="AIzaasdf")
        sig = inspect.signature(client.reverse_geocode)
        self.assertIn(
            "enable_address_descriptor",
            sig.parameters,
            "Client.reverse_geocode must expose enable_address_descriptor "
            "(regression for issue #540).",
        )

    def test_client_method_call_does_not_raise_typeerror(self):
        """The exact failure mode from issue #540 must no longer occur."""
        client = googlemaps.Client(key="AIzaasdf")
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                _GEOCODE_URL,
                body=_DESCRIPTOR_BODY,
                status=200,
                content_type="application/json",
            )
            try:
                client.reverse_geocode(
                    (-33.8674869, 151.2069902),
                    enable_address_descriptor=True,
                )
            except TypeError as exc:  # pragma: no cover - regression guard
                self.fail(
                    "reverse_geocode raised TypeError for "
                    "enable_address_descriptor (issue #540): %s" % exc
                )


class ReverseGeocodeAddressDescriptorTest(TestCase):
    def setUp(self):
        self.key = "AIzaasdf"
        self.client = googlemaps.Client(self.key)

    @responses.activate
    def test_flag_true_sends_lowercase_true(self):
        responses.add(
            responses.GET, _GEOCODE_URL,
            body=_DESCRIPTOR_BODY, status=200,
            content_type="application/json",
        )
        self.client.reverse_geocode(
            (-33.8674869, 151.2069902), enable_address_descriptor=True,
        )
        q = _query(responses.calls[0])
        self.assertEqual(q["enable_address_descriptor"], ["true"])
        self.assertEqual(q["latlng"], ["-33.8674869,151.2069902"])

    @responses.activate
    def test_flag_default_omits_parameter(self):
        responses.add(
            responses.GET, _GEOCODE_URL,
            body=_PLAIN_BODY, status=200,
            content_type="application/json",
        )
        self.client.reverse_geocode((-33.8674869, 151.2069902))
        q = _query(responses.calls[0])
        self.assertNotIn("enable_address_descriptor", q)

    @responses.activate
    def test_flag_false_omits_parameter(self):
        responses.add(
            responses.GET, _GEOCODE_URL,
            body=_PLAIN_BODY, status=200,
            content_type="application/json",
        )
        self.client.reverse_geocode(
            (-33.8674869, 151.2069902), enable_address_descriptor=False,
        )
        q = _query(responses.calls[0])
        self.assertNotIn("enable_address_descriptor", q)

    @responses.activate
    def test_falsy_values_omit_parameter(self):
        for falsy in (None, 0, "", [], {}):
            with self.subTest(value=falsy):
                with responses.RequestsMock() as rsps:
                    rsps.add(
                        responses.GET, _GEOCODE_URL,
                        body=_PLAIN_BODY, status=200,
                        content_type="application/json",
                    )
                    self.client.reverse_geocode(
                        (40.0, -73.0), enable_address_descriptor=falsy,
                    )
                    q = _query(rsps.calls[0])
                    self.assertNotIn("enable_address_descriptor", q)

    @responses.activate
    def test_truthy_non_bool_values_send_true(self):
        for truthy in (1, "yes", ["x"], {"a": 1}):
            with self.subTest(value=truthy):
                with responses.RequestsMock() as rsps:
                    rsps.add(
                        responses.GET, _GEOCODE_URL,
                        body=_DESCRIPTOR_BODY, status=200,
                        content_type="application/json",
                    )
                    self.client.reverse_geocode(
                        (40.0, -73.0), enable_address_descriptor=truthy,
                    )
                    q = _query(rsps.calls[0])
                    self.assertEqual(q["enable_address_descriptor"], ["true"])

    @responses.activate
    def test_combined_with_result_and_location_type(self):
        responses.add(
            responses.GET, _GEOCODE_URL,
            body=_DESCRIPTOR_BODY, status=200,
            content_type="application/json",
        )
        self.client.reverse_geocode(
            (40.714224, -73.961452),
            result_type=["street_address", "route"],
            location_type="ROOFTOP",
            language="en",
            enable_address_descriptor=True,
        )
        q = _query(responses.calls[0])
        self.assertEqual(q["enable_address_descriptor"], ["true"])
        self.assertEqual(q["result_type"], ["street_address|route"])
        self.assertEqual(q["location_type"], ["ROOFTOP"])
        self.assertEqual(q["language"], ["en"])
        self.assertEqual(q["latlng"], ["40.714224,-73.961452"])

    @responses.activate
    def test_works_with_place_id_string(self):
        place_id = "ChIJN1t_tDeuEmsRUsoyG83frY4"
        responses.add(
            responses.GET, _GEOCODE_URL,
            body=_DESCRIPTOR_BODY, status=200,
            content_type="application/json",
        )
        self.client.reverse_geocode(place_id, enable_address_descriptor=True)
        q = _query(responses.calls[0])
        self.assertEqual(q["place_id"], [place_id])
        self.assertNotIn("latlng", q)
        self.assertEqual(q["enable_address_descriptor"], ["true"])

    @responses.activate
    def test_works_with_dict_latlng(self):
        responses.add(
            responses.GET, _GEOCODE_URL,
            body=_DESCRIPTOR_BODY, status=200,
            content_type="application/json",
        )
        self.client.reverse_geocode(
            {"lat": -33.8674869, "lng": 151.2069902},
            enable_address_descriptor=True,
        )
        q = _query(responses.calls[0])
        self.assertEqual(q["latlng"], ["-33.8674869,151.2069902"])
        self.assertEqual(q["enable_address_descriptor"], ["true"])

    @responses.activate
    def test_works_with_list_latlng(self):
        responses.add(
            responses.GET, _GEOCODE_URL,
            body=_DESCRIPTOR_BODY, status=200,
            content_type="application/json",
        )
        self.client.reverse_geocode(
            [-33.8674869, 151.2069902], enable_address_descriptor=True,
        )
        q = _query(responses.calls[0])
        self.assertEqual(q["latlng"], ["-33.8674869,151.2069902"])

    @responses.activate
    def test_works_with_string_latlng(self):
        responses.add(
            responses.GET, _GEOCODE_URL,
            body=_DESCRIPTOR_BODY, status=200,
            content_type="application/json",
        )
        self.client.reverse_geocode(
            "-33.8674869,151.2069902", enable_address_descriptor=True,
        )
        q = _query(responses.calls[0])
        self.assertEqual(q["latlng"], ["-33.8674869,151.2069902"])
        self.assertEqual(q["enable_address_descriptor"], ["true"])

    @responses.activate
    def test_response_exposes_address_descriptor(self):
        responses.add(
            responses.GET, _GEOCODE_URL,
            body=_DESCRIPTOR_BODY, status=200,
            content_type="application/json",
        )
        response = self.client.reverse_geocode(
            (-33.8674869, 151.2069902), enable_address_descriptor=True,
        )
        descriptor = response.get("address_descriptor")
        self.assertIsNotNone(descriptor)
        self.assertEqual(len(descriptor["landmarks"]), 1)
        self.assertEqual(descriptor["landmarks"][0]["placeId"], "id")
        self.assertEqual(len(descriptor["areas"]), 1)

    @responses.activate
    def test_repeated_calls_are_independent(self):
        """A previous call with the flag must not leak into the next."""
        responses.add(
            responses.GET, _GEOCODE_URL,
            body=_DESCRIPTOR_BODY, status=200,
            content_type="application/json",
        )
        responses.add(
            responses.GET, _GEOCODE_URL,
            body=_PLAIN_BODY, status=200,
            content_type="application/json",
        )

        self.client.reverse_geocode(
            (40.0, -73.0), enable_address_descriptor=True,
        )
        self.client.reverse_geocode((40.0, -73.0))

        self.assertEqual(
            _query(responses.calls[0])["enable_address_descriptor"], ["true"],
        )
        self.assertNotIn(
            "enable_address_descriptor", _query(responses.calls[1]),
        )

    @responses.activate
    def test_keyword_only_call_via_module_function(self):
        """Calling the underlying module function directly must also work."""
        responses.add(
            responses.GET, _GEOCODE_URL,
            body=_DESCRIPTOR_BODY, status=200,
            content_type="application/json",
        )
        geocoding.reverse_geocode(
            self.client,
            (-33.8674869, 151.2069902),
            enable_address_descriptor=True,
        )
        q = _query(responses.calls[0])
        self.assertEqual(q["enable_address_descriptor"], ["true"])

    def test_unknown_kwarg_still_raises_typeerror(self):
        """Sanity check: only the documented kwarg is accepted."""
        client = googlemaps.Client(self.key)
        with self.assertRaises(TypeError):
            client.reverse_geocode(
                (-33.8674869, 151.2069902),
                enable_address_descriptors=True,  # note the typo / plural
            )
