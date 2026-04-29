"""Advanced parametrized tests for googlemaps.batch.BatchExecutor."""

from __future__ import annotations

import re
from urllib.parse import parse_qs, urlparse

import pytest
import responses

import googlemaps
from googlemaps.batch import BatchExecutor

# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------

def test_batch_requires_client():
    with pytest.raises(ValueError):
        BatchExecutor(None)


@pytest.mark.parametrize("bad", [0, -1, -100])
def test_batch_max_workers_validation(bad):
    c = googlemaps.Client(key="AIzaasdf")
    with pytest.raises(ValueError):
        BatchExecutor(c, max_workers=bad)


@pytest.mark.parametrize("ok", [1, 2, 4, 8, 16, 32, 64])
def test_batch_max_workers_accepted(ok):
    c = googlemaps.Client(key="AIzaasdf")
    b = BatchExecutor(c, max_workers=ok)
    assert b.max_workers == ok


def test_batch_default_max_workers_capped_at_32():
    c = googlemaps.Client(key="AIzaasdf", queries_per_second=1000)
    b = BatchExecutor(c)
    assert b.max_workers == 32


def test_batch_default_max_workers_uses_quota_when_low():
    c = googlemaps.Client(key="AIzaasdf", queries_per_second=4)
    b = BatchExecutor(c)
    assert b.max_workers == 4


@pytest.mark.parametrize("flag", [True, False])
def test_batch_return_exceptions_flag(flag):
    c = googlemaps.Client(key="AIzaasdf")
    b = BatchExecutor(c, return_exceptions=flag)
    assert b.return_exceptions is flag


# ---------------------------------------------------------------------------
# run() — empty / dispatch / unknown method
# ---------------------------------------------------------------------------

def test_batch_run_empty_inputs_no_calls():
    c = googlemaps.Client(key="AIzaasdf")
    b = BatchExecutor(c)
    assert b.run("geocode", []) == []


def test_batch_run_unknown_method_raises():
    c = googlemaps.Client(key="AIzaasdf")
    b = BatchExecutor(c)
    with pytest.raises(AttributeError):
        b.run("not_a_method", ["x"])


def test_batch_run_callable_method():
    c = googlemaps.Client(key="AIzaasdf")
    b = BatchExecutor(c)
    out = b.run(lambda v: v * 2, [1, 2, 3, 4, 5])
    assert out == [2, 4, 6, 8, 10]


@pytest.mark.parametrize("n", [1, 2, 4, 8, 16, 32, 64, 100])
def test_batch_callable_preserves_order(n):
    c = googlemaps.Client(key="AIzaasdf")
    b = BatchExecutor(c, max_workers=8)
    out = b.run(lambda v: v, list(range(n)))
    assert out == list(range(n))


# ---------------------------------------------------------------------------
# Per-item exception handling
# ---------------------------------------------------------------------------

def test_batch_return_exceptions_captures_errors():
    c = googlemaps.Client(key="AIzaasdf")
    b = BatchExecutor(c, return_exceptions=True)

    def maybe_fail(v):
        if v % 2 == 0:
            raise RuntimeError(f"boom {v}")
        return v

    out = b.run(maybe_fail, [1, 2, 3, 4, 5])
    assert out[0] == 1
    assert isinstance(out[1], RuntimeError)
    assert out[2] == 3
    assert isinstance(out[3], RuntimeError)
    assert out[4] == 5


def test_batch_return_exceptions_false_propagates():
    c = googlemaps.Client(key="AIzaasdf")
    b = BatchExecutor(c, return_exceptions=False, max_workers=1)
    with pytest.raises(ZeroDivisionError):
        b.run(lambda v: 1 / 0, [1])


@pytest.mark.parametrize("exc_type", [ValueError, RuntimeError, KeyError, TypeError])
def test_batch_captures_various_exception_types(exc_type):
    c = googlemaps.Client(key="AIzaasdf")
    b = BatchExecutor(c, return_exceptions=True)
    out = b.run(lambda v: (_ for _ in ()).throw(exc_type("e")), [1])
    assert isinstance(out[0], exc_type)


# ---------------------------------------------------------------------------
# common_kwargs / unpack
# ---------------------------------------------------------------------------

def test_batch_common_kwargs_forwarded():
    c = googlemaps.Client(key="AIzaasdf")
    b = BatchExecutor(c, max_workers=2)
    out = b.run(lambda v, suffix: f"{v}{suffix}", ["a", "b", "c"], common_kwargs={"suffix": "!"})
    assert out == ["a!", "b!", "c!"]


def test_batch_unpack_pairs():
    c = googlemaps.Client(key="AIzaasdf")
    b = BatchExecutor(c, max_workers=2)
    out = b.run(lambda x, y: x + y, [(1, 2), (3, 4), (5, 6)], unpack=True)
    assert out == [3, 7, 11]


def test_batch_no_unpack_passes_tuple():
    c = googlemaps.Client(key="AIzaasdf")
    b = BatchExecutor(c, max_workers=2)
    out = b.run(lambda pair: pair, [(1, 2), (3, 4)])
    assert out == [(1, 2), (3, 4)]


# ---------------------------------------------------------------------------
# Real geocode batch via responses (URL-driven)
# ---------------------------------------------------------------------------

@responses.activate
def test_batch_geocode_preserves_order():
    def callback(request):
        addr = parse_qs(urlparse(request.url).query)["address"][0]
        body = (
            '{"status":"OK","results":[{"formatted_address":"' + addr + ' (resolved)"}]}'
        )
        return (200, {"Content-Type": "application/json"}, body)

    responses.add_callback(
        responses.GET,
        "https://maps.googleapis.com/maps/api/geocode/json",
        callback=callback,
        content_type="application/json",
    )
    c = googlemaps.Client(key="AIzaasdf", queries_per_second=10)
    b = BatchExecutor(c, max_workers=4)
    inputs = ["Sydney", "Melbourne", "Perth", "Brisbane", "Hobart"]
    results = b.geocode(inputs)
    for inp, res in zip(inputs, results):
        assert res["results"][0]["formatted_address"] == f"{inp} (resolved)"


@responses.activate
def test_batch_geocode_isolates_failure():
    def callback(request):
        addr = parse_qs(urlparse(request.url).query)["address"][0]
        if "BAD" in addr:
            return (200, {"Content-Type": "application/json"},
                    '{"status":"REQUEST_DENIED","error_message":"nope"}')
        return (200, {"Content-Type": "application/json"},
                '{"status":"OK","results":[{"formatted_address":"' + addr + '"}]}')

    responses.add_callback(
        responses.GET,
        "https://maps.googleapis.com/maps/api/geocode/json",
        callback=callback,
        content_type="application/json",
    )
    c = googlemaps.Client(key="AIzaasdf", queries_per_second=10)
    b = BatchExecutor(c, max_workers=2)
    out = b.geocode(["Sydney", "BAD", "Perth"])
    assert out[0]["results"][0]["formatted_address"] == "Sydney"
    assert isinstance(out[1], googlemaps.exceptions.ApiError)
    assert out[2]["results"][0]["formatted_address"] == "Perth"


# ---------------------------------------------------------------------------
# Shortcut routing
# ---------------------------------------------------------------------------

@responses.activate
@pytest.mark.parametrize("n", [1, 3, 5, 8])
def test_batch_geocode_request_count(n):
    responses.add_callback(
        responses.GET,
        "https://maps.googleapis.com/maps/api/geocode/json",
        callback=lambda r: (200, {"Content-Type": "application/json"},
                            '{"status":"OK","results":[]}'),
    )
    c = googlemaps.Client(key="AIzaasdf", queries_per_second=10)
    b = BatchExecutor(c, max_workers=4)
    b.geocode([f"addr-{i}" for i in range(n)])
    assert len(responses.calls) == n


@responses.activate
def test_batch_reverse_geocode_url():
    responses.add_callback(
        responses.GET,
        "https://maps.googleapis.com/maps/api/geocode/json",
        callback=lambda r: (200, {"Content-Type": "application/json"},
                            '{"status":"OK","results":[]}'),
    )
    c = googlemaps.Client(key="AIzaasdf")
    b = BatchExecutor(c, max_workers=2)
    b.reverse_geocode([(1.0, 2.0), (3.0, 4.0)])
    urls = [call.request.url for call in responses.calls]
    assert any("latlng=1" in u for u in urls)
    assert any("latlng=3" in u for u in urls)


@responses.activate
def test_batch_common_kwargs_appears_in_url():
    responses.add_callback(
        responses.GET,
        "https://maps.googleapis.com/maps/api/geocode/json",
        callback=lambda r: (200, {"Content-Type": "application/json"},
                            '{"status":"OK","results":[]}'),
    )
    c = googlemaps.Client(key="AIzaasdf")
    b = BatchExecutor(c, max_workers=2)
    b.run("geocode", ["Sydney"], common_kwargs={"region": "au"})
    assert "region=au" in responses.calls[0].request.url


# ---------------------------------------------------------------------------
# Larger inputs / stress
# ---------------------------------------------------------------------------

@responses.activate
@pytest.mark.parametrize("count,workers", [
    (10, 2),
    (20, 4),
    (50, 8),
    (100, 16),
])
def test_batch_many_inputs(count, workers):
    responses.add_callback(
        responses.GET,
        "https://maps.googleapis.com/maps/api/geocode/json",
        callback=lambda r: (
            200,
            {"Content-Type": "application/json"},
            '{"status":"OK","results":[{"formatted_address":"x"}]}',
        ),
    )
    c = googlemaps.Client(key="AIzaasdf", queries_per_second=count)
    b = BatchExecutor(c, max_workers=workers)
    out = b.geocode([f"in-{i}" for i in range(count)])
    assert len(out) == count
    # geocode returns the response body (dict with a "results" key).
    assert all(isinstance(r, dict) and "results" in r for r in out)


# Avoid unused import warning when re-imported above.
_ = re
