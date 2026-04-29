#
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#

"""Tests for googlemaps.batch.BatchExecutor."""

import time

import pytest
import responses

import googlemaps
from googlemaps.batch import BatchExecutor


def _make_client():
    return googlemaps.Client(key="AIzaTEST")


class TestBatchExecutorConstruction:
    def test_requires_client(self):
        with pytest.raises(ValueError):
            BatchExecutor(None)

    def test_max_workers_validated(self):
        with pytest.raises(ValueError):
            BatchExecutor(_make_client(), max_workers=0)

    def test_default_max_workers_capped_at_32(self):
        c = _make_client()
        c.queries_quota = 999
        b = BatchExecutor(c)
        assert b.max_workers == 32

    def test_default_max_workers_uses_quota_when_low(self):
        c = _make_client()
        c.queries_quota = 4
        assert BatchExecutor(c).max_workers == 4


class TestBatchExecutorRun:
    @responses.activate
    def test_geocode_batch_preserves_order(self):
        # Use a URL-driven callback so each thread gets the response that
        # matches its own query — concurrent execution otherwise scrambles
        # which stub serves which request.
        from urllib.parse import parse_qs, urlparse

        def _callback(request):
            qs = parse_qs(urlparse(request.url).query)
            city = qs["address"][0]
            return (200, {}, '{"status":"OK","results":[{"formatted_address":"' + city + '"}]}')

        responses.add_callback(
            responses.GET,
            "https://maps.googleapis.com/maps/api/geocode/json",
            callback=_callback,
            content_type="application/json",
        )
        gmaps = _make_client()
        batch = BatchExecutor(gmaps, max_workers=4)
        results = batch.geocode(["Sydney", "Melbourne", "Perth"])
        assert len(results) == 3
        addrs = [r["results"][0]["formatted_address"] for r in results]
        assert addrs == ["Sydney", "Melbourne", "Perth"]

    @responses.activate
    def test_empty_inputs_no_calls(self):
        batch = BatchExecutor(_make_client())
        assert batch.run("geocode", []) == []
        assert len(responses.calls) == 0

    @responses.activate
    def test_return_exceptions_captures_per_item_errors(self):
        # First call OK, second triggers ApiError via INVALID_REQUEST.
        responses.add(
            responses.GET,
            "https://maps.googleapis.com/maps/api/geocode/json",
            json={"status": "OK", "results": [{"formatted_address": "Sydney"}]},
            status=200,
        )
        responses.add(
            responses.GET,
            "https://maps.googleapis.com/maps/api/geocode/json",
            json={"status": "INVALID_REQUEST", "error_message": "bad input"},
            status=200,
        )
        gmaps = _make_client()
        batch = BatchExecutor(gmaps, max_workers=1)  # serialize for determinism
        results = batch.geocode(["Sydney", "BAD"])
        assert isinstance(results[0], dict)
        assert isinstance(results[1], googlemaps.exceptions.ApiError)

    @responses.activate
    def test_return_exceptions_false_propagates(self):
        responses.add(
            responses.GET,
            "https://maps.googleapis.com/maps/api/geocode/json",
            json={"status": "INVALID_REQUEST", "error_message": "bad input"},
            status=200,
        )
        gmaps = _make_client()
        batch = BatchExecutor(gmaps, max_workers=1, return_exceptions=False)
        with pytest.raises(googlemaps.exceptions.ApiError):
            batch.geocode(["BAD"])

    @responses.activate
    def test_unknown_method_raises(self):
        batch = BatchExecutor(_make_client())
        with pytest.raises(AttributeError):
            batch.run("does_not_exist", ["x"])

    @responses.activate
    def test_callable_method(self):
        gmaps = _make_client()

        def custom(value):
            return value * 2

        batch = BatchExecutor(gmaps, max_workers=2)
        out = batch.run(custom, [1, 2, 3])
        # The custom callable receives only the item — the client is not
        # auto-injected. Callers can close over the client if they need it.
        assert out == [2, 4, 6]

    @responses.activate
    def test_unpack_for_directions(self):
        responses.add(
            responses.GET,
            "https://maps.googleapis.com/maps/api/directions/json",
            json={"status": "OK", "routes": [{"summary": "A->B"}]},
            status=200,
        )
        responses.add(
            responses.GET,
            "https://maps.googleapis.com/maps/api/directions/json",
            json={"status": "OK", "routes": [{"summary": "C->D"}]},
            status=200,
        )
        gmaps = _make_client()
        batch = BatchExecutor(gmaps, max_workers=1)
        results = batch.directions([("A", "B"), ("C", "D")])
        assert results[0][0]["summary"] == "A->B"
        assert results[1][0]["summary"] == "C->D"

    @responses.activate
    def test_common_kwargs_forwarded(self):
        responses.add(
            responses.GET,
            "https://maps.googleapis.com/maps/api/geocode/json",
            json={"status": "OK", "results": []},
            status=200,
        )
        gmaps = _make_client()
        batch = BatchExecutor(gmaps, max_workers=1)
        batch.geocode(["Sydney"], region="au")
        # Verify language param made it onto the request URL.
        assert "region=au" in responses.calls[0].request.url


class TestBatchExecutorConcurrency:
    @responses.activate
    def test_concurrent_execution_is_faster_than_serial(self):
        """Sanity: 8 calls each delayed 100ms should take well under 800ms."""
        delay = 0.1
        N = 8

        def slow(_request):
            time.sleep(delay)
            return (200, {}, '{"status":"OK","results":[]}')

        responses.add_callback(
            responses.GET,
            "https://maps.googleapis.com/maps/api/geocode/json",
            callback=slow,
            content_type="application/json",
        )
        gmaps = _make_client()
        # Disable QPS throttling for this test to measure pure parallelism.
        gmaps.queries_quota = N
        batch = BatchExecutor(gmaps, max_workers=N)
        start = time.monotonic()
        results = batch.geocode([f"city-{i}" for i in range(N)])
        elapsed = time.monotonic() - start
        assert len(results) == N
        # Serial would be N*delay = 0.8s; concurrent should be < 0.5s.
        assert elapsed < (N * delay) * 0.6, f"Took {elapsed:.3f}s, expected concurrency"

    @responses.activate
    def test_runs_safely_with_many_workers(self):
        """No deadlock / data corruption when threads outnumber items."""
        responses.add(
            responses.GET,
            "https://maps.googleapis.com/maps/api/geocode/json",
            json={"status": "OK", "results": []},
            status=200,
        )
        gmaps = _make_client()
        batch = BatchExecutor(gmaps, max_workers=16)
        out = batch.geocode([f"q{i}" for i in range(3)])
        assert len(out) == 3
