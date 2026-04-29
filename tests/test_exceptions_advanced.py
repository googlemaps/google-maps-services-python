"""Advanced parametrized tests for googlemaps.exceptions."""

from __future__ import annotations

import pytest

from googlemaps import exceptions as exc

# ---------------------------------------------------------------------------
# ApiError
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "status,message,expected",
    [
        ("OVER_QUERY_LIMIT", "rate limited", "OVER_QUERY_LIMIT (rate limited)"),
        ("INVALID_REQUEST", "bad", "INVALID_REQUEST (bad)"),
        ("REQUEST_DENIED", "denied", "REQUEST_DENIED (denied)"),
        ("UNKNOWN_ERROR", "??", "UNKNOWN_ERROR (??)"),
        ("NOT_FOUND", "missing", "NOT_FOUND (missing)"),
    ],
)
def test_apierror_with_message(status, message, expected):
    err = exc.ApiError(status, message)
    assert str(err) == expected
    assert err.status == status
    assert err.message == message


@pytest.mark.parametrize(
    "status",
    ["OK", "ZERO_RESULTS", "OVER_QUERY_LIMIT", "INVALID_REQUEST", "REQUEST_DENIED"],
)
def test_apierror_without_message(status):
    err = exc.ApiError(status)
    assert str(err) == status
    assert err.message is None


def test_apierror_is_exception():
    assert issubclass(exc.ApiError, Exception)


def test_apierror_can_be_raised_and_caught():
    with pytest.raises(exc.ApiError) as ei:
        raise exc.ApiError("BOOM", "kaboom")
    assert ei.value.status == "BOOM"


# ---------------------------------------------------------------------------
# TransportError
# ---------------------------------------------------------------------------

def test_transport_error_default_message():
    err = exc.TransportError()
    assert str(err) == "An unknown error occurred."


@pytest.mark.parametrize(
    "base,expected",
    [
        (RuntimeError("boom"), "boom"),
        (ValueError("bad"), "bad"),
        (ConnectionError("net"), "net"),
        (TimeoutError("slow"), "slow"),
        (OSError("io"), "io"),
    ],
)
def test_transport_error_wraps_base(base, expected):
    err = exc.TransportError(base)
    assert str(err) == expected
    assert err.base_exception is base


def test_transport_error_is_exception():
    assert issubclass(exc.TransportError, Exception)


# ---------------------------------------------------------------------------
# HTTPError
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "code,expected",
    [
        (400, "HTTP Error: 400"),
        (401, "HTTP Error: 401"),
        (403, "HTTP Error: 403"),
        (404, "HTTP Error: 404"),
        (500, "HTTP Error: 500"),
        (502, "HTTP Error: 502"),
        (503, "HTTP Error: 503"),
        (504, "HTTP Error: 504"),
    ],
)
def test_http_error_str(code, expected):
    err = exc.HTTPError(code)
    assert str(err) == expected
    assert err.status_code == code


def test_http_error_is_transport_error():
    assert issubclass(exc.HTTPError, exc.TransportError)


# ---------------------------------------------------------------------------
# Timeout / retriable
# ---------------------------------------------------------------------------

def test_timeout_is_exception():
    assert issubclass(exc.Timeout, Exception)


def test_timeout_raisable():
    with pytest.raises(exc.Timeout):
        raise exc.Timeout()


def test_retriable_request_is_exception():
    assert issubclass(exc._RetriableRequest, Exception)


def test_over_query_limit_is_apierror_and_retriable():
    err = exc._OverQueryLimit("OVER_QUERY_LIMIT", "rate")
    assert isinstance(err, exc.ApiError)
    assert isinstance(err, exc._RetriableRequest)


def test_over_query_limit_string_includes_message():
    err = exc._OverQueryLimit("OVER_QUERY_LIMIT", "rate")
    assert "OVER_QUERY_LIMIT" in str(err)
    assert "rate" in str(err)
