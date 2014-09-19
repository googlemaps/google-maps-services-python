# TODO: move to test_common when PR #8 is merged.

import googlemaps
import unittest
import responses

class UATest(unittest.TestCase):

    @responses.activate
    def test_ua_sent(self):
        responses.add(responses.GET,
                      "https://maps.googleapis.com/maps/api/geocode/json",
                      body='{"status":"OK","results":[]}',
                      status=200,
                      content_type='application/json')

        ctx = googlemaps.Context(key="AIzaasdf")
        googlemaps.geocode(ctx, "Sesame St.")

        self.assertEquals(1, len(responses.calls))
        user_agent = responses.calls[0].request.headers["User-Agent"]
        self.assertTrue(user_agent.startswith("GoogleGeoApiClientPython"))
