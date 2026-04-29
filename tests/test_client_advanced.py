"""Advanced parametrized tests for googlemaps.client core helpers."""

from __future__ import annotations

import pytest
import responses

import googlemaps
from googlemaps import client as _client
from googlemaps.client import (
    _X_GOOG_MAPS_EXPERIENCE_ID,
    normalize_for_urlencode,
    sign_hmac,
    urlencode_params,
)

# ---------------------------------------------------------------------------
# Constructor — credentials
# ---------------------------------------------------------------------------

def test_client_no_credentials_raises():
    with pytest.raises(ValueError):
        googlemaps.Client()


@pytest.mark.parametrize(
    "bad_key", ["", "no-prefix", "abc", "1234567890", "AIz", "key-without-AIza"],
)
def test_invalid_api_key_format(bad_key):
    with pytest.raises(ValueError):
        googlemaps.Client(key=bad_key)


@pytest.mark.parametrize(
    "good_key",
    [
        "AIza" + "x" * 35,
        "AIza1234",
        "AIzaA",
        "AIzaSyA-abc_def-12345",
    ],
)
def test_valid_api_key_format(good_key):
    c = googlemaps.Client(key=good_key)
    assert c.key == good_key


def test_client_with_enterprise_only():
    c = googlemaps.Client(client_id="me", client_secret="c2VjcmV0")
    assert c.client_id == "me"


# ---------------------------------------------------------------------------
# Constructor — channel validation
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "ch",
    ["abc", "ABC", "abc123", "abc.123", "a-b_c.d", "", "channel0", "0"],
)
def test_valid_channel(ch):
    googlemaps.Client(client_id="me", client_secret="c2VjcmV0", channel=ch)


@pytest.mark.parametrize(
    "ch",
    ["bad channel", "with/slash", "with#hash", "café", "with space", "?"],
)
def test_invalid_channel(ch):
    with pytest.raises(ValueError):
        googlemaps.Client(client_id="me", client_secret="c2VjcmV0", channel=ch)


# ---------------------------------------------------------------------------
# Constructor — timeouts
# ---------------------------------------------------------------------------

def test_timeout_combined_with_split_raises():
    with pytest.raises(ValueError):
        googlemaps.Client(key="AIzaasdf", timeout=10, connect_timeout=5)


def test_timeout_combined_with_split_read_raises():
    with pytest.raises(ValueError):
        googlemaps.Client(key="AIzaasdf", timeout=10, read_timeout=5)


def test_split_timeouts():
    c = googlemaps.Client(key="AIzaasdf", connect_timeout=2, read_timeout=10)
    assert c.timeout == (2, 10)


def test_simple_timeout():
    c = googlemaps.Client(key="AIzaasdf", timeout=5)
    assert c.timeout == 5


# ---------------------------------------------------------------------------
# Constructor — QPS / QPM
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "qps,qpm,expected",
    [
        (60, 6000, 60),  # qps wins (qpm/60 = 100 > 60)
        (10, 6000, 10),
        (60, 60, 1),  # qpm/60 = 1
        (1, 6000, 1),
        (100, 600, 10),  # qpm/60 = 10
        (50, 60, 1),
    ],
)
def test_queries_quota_min_of_both(qps, qpm, expected):
    c = googlemaps.Client(key="AIzaasdf", queries_per_second=qps, queries_per_minute=qpm)
    assert c.queries_quota == expected


def test_queries_quota_qps_only():
    c = googlemaps.Client(key="AIzaasdf", queries_per_second=42, queries_per_minute=None)
    assert c.queries_quota == 42


def test_queries_quota_qpm_only():
    c = googlemaps.Client(key="AIzaasdf", queries_per_second=None, queries_per_minute=120)
    assert c.queries_quota == 2


def test_queries_quota_neither_raises():
    with pytest.raises(ValueError):
        googlemaps.Client(key="AIzaasdf", queries_per_second=None, queries_per_minute=None)


# ---------------------------------------------------------------------------
# experience_id
# ---------------------------------------------------------------------------

def test_experience_id_set_and_get():
    c = googlemaps.Client(key="AIzaasdf", experience_id="exp-1")
    assert c.get_experience_id() == "exp-1"


def test_experience_id_multi_value():
    c = googlemaps.Client(key="AIzaasdf")
    c.set_experience_id("exp-1", "exp-2")
    assert c.get_experience_id() == "exp-1,exp-2"


def test_experience_id_clear():
    c = googlemaps.Client(key="AIzaasdf", experience_id="exp-1")
    c.clear_experience_id()
    assert c.get_experience_id() is None


def test_experience_id_init_none():
    c = googlemaps.Client(key="AIzaasdf")
    assert c.get_experience_id() is None


def test_set_experience_id_none_clears():
    c = googlemaps.Client(key="AIzaasdf", experience_id="exp-1")
    c.set_experience_id(None)
    assert c.get_experience_id() is None


def test_set_experience_id_empty_args_clears():
    c = googlemaps.Client(key="AIzaasdf", experience_id="exp-1")
    c.set_experience_id()
    assert c.get_experience_id() is None


def test_experience_id_header_key():
    c = googlemaps.Client(key="AIzaasdf", experience_id="exp-1")
    headers = c.requests_kwargs["headers"]
    assert headers[_X_GOOG_MAPS_EXPERIENCE_ID] == "exp-1"


# ---------------------------------------------------------------------------
# urlencode_params / normalize_for_urlencode
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "params,expected",
    [
        ([("a", "1")], "a=1"),
        ([("a", "1"), ("b", "2")], "a=1&b=2"),
        ([("address", "=Sydney ~")], "address=%3DSydney+~"),
        ([("k", "")], "k="),
        ([("k", ["a", "b"])], "k=a&k=b"),
        ([("k", ("x", "y"))], "k=x&k=y"),
        ([("k", 42)], "k=42"),
        ([("k", 1.5)], "k=1.5"),
        ([("k", True)], "k=True"),
        ([("k", None)], "k=None"),
    ],
)
def test_urlencode_params(params, expected):
    assert urlencode_params(params) == expected


@pytest.mark.parametrize(
    "value,expected",
    [
        ("hello", "hello"),
        (42, "42"),
        (1.5, "1.5"),
        (True, "True"),
        (None, "None"),
        ("", ""),
        ("café", "café"),
    ],
)
def test_normalize_for_urlencode(value, expected):
    assert normalize_for_urlencode(value) == expected


# ---------------------------------------------------------------------------
# sign_hmac
# ---------------------------------------------------------------------------

def test_sign_hmac_deterministic():
    secret = "vNIXE0xscrmjlyV-12Nj_BvUPaw="
    sig_a = sign_hmac(secret, "/path?key=value")
    sig_b = sign_hmac(secret, "/path?key=value")
    assert sig_a == sig_b


def test_sign_hmac_different_payloads_differ():
    secret = "vNIXE0xscrmjlyV-12Nj_BvUPaw="
    assert sign_hmac(secret, "/a") != sign_hmac(secret, "/b")


def test_sign_hmac_returns_str():
    out = sign_hmac("vNIXE0xscrmjlyV-12Nj_BvUPaw=", "/x")
    assert isinstance(out, str)
    assert len(out) > 0


# ---------------------------------------------------------------------------
# auth url construction (integration-y, but stays cheap)
# ---------------------------------------------------------------------------

@responses.activate
def test_request_includes_key_in_url():
    responses.add(
        responses.GET,
        "https://maps.googleapis.com/maps/api/geocode/json",
        body='{"status":"OK","results":[]}',
        status=200,
        content_type="application/json",
    )
    c = googlemaps.Client(key="AIzaasdf")
    c.geocode("Sydney")
    assert "key=AIzaasdf" in responses.calls[0].request.url


@responses.activate
def test_request_with_clientid_includes_signature_and_client():
    responses.add(
        responses.GET,
        "https://maps.googleapis.com/maps/api/geocode/json",
        body='{"status":"OK","results":[]}',
        status=200,
        content_type="application/json",
    )
    c = googlemaps.Client(client_id="me", client_secret="vNIXE0xscrmjlyV-12Nj_BvUPaw=")
    c.geocode("Sydney")
    url = responses.calls[0].request.url
    assert "client=me" in url
    assert "signature=" in url


@responses.activate
def test_request_with_channel_in_url():
    responses.add(
        responses.GET,
        "https://maps.googleapis.com/maps/api/geocode/json",
        body='{"status":"OK","results":[]}',
        status=200,
        content_type="application/json",
    )
    c = googlemaps.Client(
        client_id="me", client_secret="vNIXE0xscrmjlyV-12Nj_BvUPaw=", channel="my.channel"
    )
    c.geocode("Sydney")
    assert "channel=my.channel" in responses.calls[0].request.url


# ---------------------------------------------------------------------------
# retry behavior (5xx)
# ---------------------------------------------------------------------------

@responses.activate
def test_retriable_5xx_then_success():
    responses.add(
        responses.GET,
        "https://maps.googleapis.com/maps/api/geocode/json",
        body="server error", status=500,
    )
    responses.add(
        responses.GET,
        "https://maps.googleapis.com/maps/api/geocode/json",
        body='{"status":"OK","results":[]}',
        status=200,
        content_type="application/json",
    )
    c = googlemaps.Client(key="AIzaasdf", retry_timeout=10)
    c.geocode("Sydney")
    assert len(responses.calls) == 2


@responses.activate
def test_non_retriable_4xx_raises_http_error():
    responses.add(
        responses.GET,
        "https://maps.googleapis.com/maps/api/geocode/json",
        body="bad", status=400,
    )
    c = googlemaps.Client(key="AIzaasdf")
    with pytest.raises(googlemaps.exceptions.HTTPError):
        c.geocode("Sydney")


@responses.activate
def test_api_error_raised_for_non_ok_status():
    responses.add(
        responses.GET,
        "https://maps.googleapis.com/maps/api/geocode/json",
        body='{"status":"REQUEST_DENIED","error_message":"nope"}',
        status=200,
        content_type="application/json",
    )
    c = googlemaps.Client(key="AIzaasdf")
    with pytest.raises(googlemaps.exceptions.ApiError) as ei:
        c.geocode("Sydney")
    assert ei.value.status == "REQUEST_DENIED"


@responses.activate
def test_zero_results_does_not_raise():
    responses.add(
        responses.GET,
        "https://maps.googleapis.com/maps/api/geocode/json",
        body='{"status":"ZERO_RESULTS","results":[]}',
        status=200,
        content_type="application/json",
    )
    c = googlemaps.Client(key="AIzaasdf")
    # Does not raise; body is returned (results may be empty list).
    out = c.geocode("Atlantis")
    assert out in ([], {"status": "ZERO_RESULTS", "results": []})


@responses.activate
def test_over_query_limit_no_retry():
    responses.add(
        responses.GET,
        "https://maps.googleapis.com/maps/api/geocode/json",
        body='{"status":"OVER_QUERY_LIMIT"}',
        status=200,
        content_type="application/json",
    )
    c = googlemaps.Client(key="AIzaasdf", retry_over_query_limit=False)
    with pytest.raises(googlemaps.exceptions._OverQueryLimit):
        c.geocode("Sydney")


# ---------------------------------------------------------------------------
# extra_params (advanced unsupported feature)
# ---------------------------------------------------------------------------

@responses.activate
def test_extra_params_appears_in_url():
    responses.add(
        responses.GET,
        "https://maps.googleapis.com/maps/api/geocode/json",
        body='{"status":"OK","results":[]}',
        status=200,
        content_type="application/json",
    )
    c = googlemaps.Client(key="AIzaasdf")
    c.geocode("Sydney", extra_params={"foo": "bar"})
    assert "foo=bar" in responses.calls[0].request.url
    # extra_params is consumed, so subsequent calls don't carry it.
    assert not hasattr(c, "_extra_params")


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

def test_user_agent_constant_includes_version():
    assert googlemaps.__version__ in _client._USER_AGENT
    assert "GoogleGeoApiClientPython" in _client._USER_AGENT


def test_default_base_url_is_https_googleapis():
    assert _client._DEFAULT_BASE_URL.startswith("https://")
    assert "googleapis.com" in _client._DEFAULT_BASE_URL


@pytest.mark.parametrize("status", [500, 503, 504])
def test_retriable_statuses_constant(status):
    assert status in _client._RETRIABLE_STATUSES


@pytest.mark.parametrize("status", [200, 400, 401, 403, 404, 502])
def test_non_retriable_statuses(status):
    assert status not in _client._RETRIABLE_STATUSES
