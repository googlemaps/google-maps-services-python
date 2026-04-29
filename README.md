Python Client for Google Maps Services
====================================

![Test](https://github.com/googlemaps/google-maps-services-js/workflows/Test/badge.svg)
![Release](https://github.com/googlemaps/google-maps-services-js/workflows/Release/badge.svg)
[![codecov](https://codecov.io/gh/googlemaps/google-maps-services-python/branch/master/graph/badge.svg)](https://codecov.io/gh/googlemaps/google-maps-services-python)
[![PyPI version](https://badge.fury.io/py/googlemaps.svg)](https://badge.fury.io/py/googlemaps)
![PyPI - Downloads](https://img.shields.io/pypi/dd/googlemaps)
![GitHub contributors](https://img.shields.io/github/contributors/googlemaps/google-maps-services-python)

> **Fork notice.** This repository is a community fork that layers two
> production-grade additions on top of the official client — a **pluggable
> response cache** and a **concurrent batch executor** — without changing
> any existing public surface. Drop-in compatible: existing code keeps
> working unchanged.

---

## Table of contents

- [Description](#description)
- [Supported Google Maps Web Services](#supported-google-maps-web-services)
- [Requirements](#requirements)
- [Installation](#installation)
- [API keys](#api-keys)
- [Quick start](#quick-start)
- [Built-in features](#built-in-features)
  - [Retry on failure](#retry-on-failure)
  - [Rate limiting (QPS / QPM)](#rate-limiting-qps--qpm)
- [Fork additions](#fork-additions)
  - [1. Pluggable response cache (TTL + LRU)](#1-pluggable-response-cache-ttl--lru)
  - [2. Concurrent batch executor](#2-concurrent-batch-executor)
  - [Composing both features](#composing-both-features)
- [Development workflow](#development-workflow)
- [Project layout](#project-layout)
- [Quality bar](#quality-bar)
- [Documentation & resources](#documentation--resources)
- [Support](#support)

---

## Description

The Python Client for Google Maps Services brings the Google Maps Platform
Web Services to your Python application — geocoding, directions, places,
elevation, time zones, roads, and more. The same
[terms and conditions](https://developers.google.com/maps/terms) apply to
usage of the APIs through this library.

### Supported Google Maps Web Services

| API | Module | Client method(s) |
| --- | --- | --- |
| Directions API           | [googlemaps/directions.py](googlemaps/directions.py)             | `directions` |
| Distance Matrix API      | [googlemaps/distance_matrix.py](googlemaps/distance_matrix.py)   | `distance_matrix` |
| Elevation API            | [googlemaps/elevation.py](googlemaps/elevation.py)               | `elevation`, `elevation_along_path` |
| Geocoding API            | [googlemaps/geocoding.py](googlemaps/geocoding.py)               | `geocode`, `reverse_geocode` |
| Geolocation API          | [googlemaps/geolocation.py](googlemaps/geolocation.py)           | `geolocate` |
| Time Zone API            | [googlemaps/timezone.py](googlemaps/timezone.py)                 | `timezone` |
| Roads API                | [googlemaps/roads.py](googlemaps/roads.py)                       | `snap_to_roads`, `nearest_roads`, `speed_limits`, `snapped_speed_limits` |
| Places API               | [googlemaps/places.py](googlemaps/places.py)                     | `find_place`, `place`, `places`, `places_nearby`, `places_photo`, `places_autocomplete`, `places_autocomplete_query` |
| Maps Static API          | [googlemaps/maps.py](googlemaps/maps.py)                         | `static_map` |
| Address Validation API   | [googlemaps/addressvalidation.py](googlemaps/addressvalidation.py) | `addressvalidation` |

---

## Requirements

- **Python 3.8+** (the fork targets modern interpreters; legacy Python 2 code paths have been removed).
- A Google Maps API key — see [API keys](#api-keys).
- `requests >= 2.20` (installed automatically).

## Installation

```bash
pip install -U googlemaps
```

For the fork (with the cache + batch executor) and a development setup:

```bash
git clone https://github.com/<your-org>/google-maps-services-python.git
cd google-maps-services-python
pip install -e ".[dev]"
```

## API keys

Each Google Maps Web Service request requires an API key or client ID. API keys
are generated in the **Credentials** page of the **APIs & Services** tab of the
[Google Cloud console](https://console.cloud.google.com/apis/credentials).
For more on getting started and key restriction, see
[Get Started with Google Maps Platform](https://developers.google.com/maps/gmp-get-started).

> **Important:** API keys must be kept secret. Use environment variables or a
> secrets manager — never commit them to source control.

---

## Quick start

```python
import googlemaps
from datetime import datetime

gmaps = googlemaps.Client(key="AIza...")

# Geocoding an address
geocode_result = gmaps.geocode("1600 Amphitheatre Parkway, Mountain View, CA")

# Reverse geocoding
reverse_geocode_result = gmaps.reverse_geocode((40.714224, -73.961452))

# Directions via public transit
now = datetime.now()
directions_result = gmaps.directions(
    "Sydney Town Hall", "Parramatta, NSW",
    mode="transit", departure_time=now,
)

# Address Validation
addressvalidation_result = gmaps.addressvalidation(
    ["1600 Amphitheatre Pk"],
    regionCode="US", locality="Mountain View", enableUspsCass=True,
)

# Address Descriptor in a reverse geocoding response
ad_result = gmaps.reverse_geocode(
    (40.714224, -73.961452), enable_address_descriptor=True,
)
```

For more usage examples see the [tests/](tests) directory.

---

## Built-in features

### Retry on failure

Idempotent requests are automatically retried on transient
**500 / 503 / 504** responses with exponential back-off and jitter, capped
at the per-client `retry_timeout` (default 60 s).

### Rate limiting (QPS / QPM)

Both `queries_per_second` and `queries_per_minute` are honoured client-side.
The effective per-second quota is the minimum of the two; the client sleeps
before issuing a request when the deque of recent calls is full.
Use `retry_over_query_limit=False` to fail fast on `OVER_QUERY_LIMIT`
instead of the default exponential-backoff retry.

```python
gmaps = googlemaps.Client(
    key="AIza...",
    queries_per_second=50,
    queries_per_minute=1500,
    retry_timeout=30,
    retry_over_query_limit=True,
)
```

---

## Fork additions

The fork ships **two** non-invasive additions that solve the most common
production pain points: avoiding repeated billed calls during development and
batch jobs, and turning the inherently serial client into an order-preserving
parallel one. Both are opt-in — the default behaviour of the upstream client
is preserved 1-for-1.

### 1. Pluggable response cache (TTL + LRU)

> **Module:** [googlemaps/cache.py](googlemaps/cache.py)
> **Public surface:** `googlemaps.BaseCache`, `googlemaps.InMemoryTTLCache`, `googlemaps.CacheStats`

#### Why

In day-to-day development, batch ETL jobs, and the test suite of any
application that uses Maps Platform, the same `(path, params)` is requested
hundreds or thousands of times. Each repeat is billed and adds latency.
A small in-process cache returns identical responses immediately — no network
trip, no quota usage — while remaining **safe by default** so it cannot
accidentally cache write/error responses.

#### Design at a glance

| Concern | How it's handled |
| --- | --- |
| **Cache key**          | `(path, sorted_params)` with auth params (`key`, `client`, `signature`, `channel`) **stripped** so the cache is shareable across credentials and stable across test runs. |
| **What is cached**     | First-attempt `GET` requests whose API status is `OK` or `ZERO_RESULTS`. |
| **What is *never* cached** | `POST` endpoints (e.g. Geolocation), retried requests, `extract_body` overrides (e.g. binary Static Maps), and any non-`OK` API response. |
| **Eviction**           | LRU on `maxsize`, plus per-entry TTL. `get` of an expired entry deletes and reports a miss. |
| **Concurrency**        | Backed by `OrderedDict` + `threading.RLock`; covered by multi-thread stress tests (8 threads × 200 ops). |
| **Observability**      | `cache.stats()` returns a snapshot `CacheStats(hits, misses, evictions, expirations, sets)` with a `hit_ratio` property. |
| **Pluggability**       | Implement `BaseCache.get/set/clear/stats` to back it with Redis, memcached, disk, etc. |

#### Usage

```python
import googlemaps
from googlemaps import InMemoryTTLCache

gmaps = googlemaps.Client(key="AIza...")
gmaps.cache = InMemoryTTLCache(maxsize=512, ttl=300)  # 5-minute TTL, 512 entries

gmaps.geocode("Sydney")               # network call -> stored
gmaps.geocode("Sydney")               # served from cache, zero billed calls

print(gmaps.cache.stats())            # CacheStats(hits=1, misses=1, sets=1, ...)
print(gmaps.cache.stats().hit_ratio)  # 0.5
```

#### Custom backend (Redis sketch)

```python
from googlemaps import BaseCache, CacheStats

class RedisCache(BaseCache):
    def __init__(self, redis_client, ttl=300):
        self._r = redis_client
        self._ttl = ttl

    def get(self, key):  # `key` is a hashable tuple — pickle / orjson it
        ...
    def set(self, key, value):
        ...
    def clear(self):
        self._r.flushdb()
    def stats(self) -> CacheStats:
        ...

gmaps.cache = RedisCache(my_redis)
```

### 2. Concurrent batch executor

> **Module:** [googlemaps/batch.py](googlemaps/batch.py)
> **Public surface:** `googlemaps.BatchExecutor`

#### Why

The Google Maps web services are synchronous — one HTTP request per call.
When you need to geocode 500 addresses or fetch directions between many
origin/destination pairs, doing them one at a time is the bottleneck.
`BatchExecutor` is a thin `ThreadPoolExecutor` wrapper that:

| Concern | Behaviour |
| --- | --- |
| **Order**              | Results are returned in the **same order** as the inputs. |
| **Quota safety**       | Each worker still hits the same `Client` rate limiter, so QPS/QPM are respected. `max_workers` defaults to `min(client.queries_quota, 32)`. |
| **Error isolation**    | Per-item exceptions are returned as `Exception` instances by default (`return_exceptions=True`) so one bad input does not poison the batch. Set `return_exceptions=False` to re-raise. |
| **Method dispatch**    | Pass any client method by **name** (`"geocode"`, `"places_nearby"`, …) or as a callable. |
| **Common kwargs**      | `common_kwargs={"region": "au"}` is forwarded to every invocation. |
| **Tuple unpacking**    | `unpack=True` unpacks paired inputs — e.g. `[(origin, destination), ...]` for `directions`. |

#### Usage

```python
import googlemaps
from googlemaps import BatchExecutor

gmaps = googlemaps.Client(key="AIza...")
batch = BatchExecutor(gmaps, max_workers=8)

# Geocode many addresses in parallel — order is preserved, errors are isolated.
queries = ["Sydney", "Melbourne", "Perth", "Bad #@! address"]
results = batch.geocode(queries)
for query, result in zip(queries, results):
    if isinstance(result, Exception):
        print(f"FAILED {query}: {result}")
    else:
        print(query, "->", result["results"][0]["formatted_address"])

# Convenience shortcuts
batch.reverse_geocode([(-33.86, 151.20), (40.71, -74.00)])
batch.directions([("A", "B"), ("C", "D")])     # tuples are unpacked
batch.place(["ChIJN1t_tDeuEmsRUsoyG83frY4"])

# Or any client method by name, with shared kwargs:
batch.run("geocode", ["Sydney", "Hobart"], common_kwargs={"region": "au"})
```

### Composing both features

The cache and batch executor are designed to compose. With both attached,
duplicate inputs in a batch are deduplicated automatically (the second
identical call is a cache hit), and the QPS limiter still gates real
network calls:

```python
gmaps = googlemaps.Client(key="AIza...", queries_per_second=20)
gmaps.cache = InMemoryTTLCache(maxsize=10_000, ttl=3600)
batch = BatchExecutor(gmaps, max_workers=16)

addresses = load_addresses_from_csv("input.csv")  # may contain duplicates
results = batch.geocode(addresses)

print(gmaps.cache.stats())  # observe hit ratio across the batch
```

---

## Development workflow

```bash
# Install dev tools and the package in editable mode
pip install -e ".[dev]"

# Run the full test suite (611 tests)
pytest

# Lint + auto-format with ruff
ruff check googlemaps tests
ruff format googlemaps tests

# Type-check
mypy

# Multi-version matrix (uses nox)
pip install nox
nox

# Generate documentation
nox -e docs

# Publish docs to gh-pages
nox -e docs && mv docs/_build/html generated_docs && \
    git clean -Xdi && git checkout gh-pages
```

## Project layout

```text
googlemaps/
  __init__.py            # public API: Client, InMemoryTTLCache, BatchExecutor, ...
  client.py              # core HTTP client, auth, retries, QPS, cache hook
  cache.py               # BaseCache + InMemoryTTLCache + CacheStats   (fork addition)
  batch.py               # BatchExecutor                               (fork addition)
  exceptions.py          # ApiError / HTTPError / Timeout / TransportError
  addressvalidation.py   # Address Validation API
  directions.py          # Directions API
  distance_matrix.py     # Distance Matrix API
  elevation.py           # Elevation API
  geocoding.py           # Geocoding API (incl. Address Descriptors)
  geolocation.py         # Geolocation API
  maps.py                # Maps Static API (StaticMapMarker / StaticMapPath)
  places.py              # Places API
  roads.py               # Roads API
  timezone.py            # Time Zone API

tests/                   # pytest suite — 611 tests, advanced parametrized coverage
  test_cache.py          # cache: API surface
  test_cache_advanced.py # cache: thread-safety, TTL with fake clock, LRU eviction order
  test_batch.py          # batch: API surface
  test_batch_advanced.py # batch: order preservation, error isolation, large workloads
  test_client_advanced.py
  test_convert_advanced.py
  test_exceptions_advanced.py
  test_maps_advanced.py
  ...

pyproject.toml           # PEP 621 metadata + ruff/pytest/coverage/mypy config
```

## Quality bar

| Metric | Status |
| --- | --- |
| Test count                  | **611 passing** (105 baseline + 506 added in this fork) |
| Lint (`ruff check`)         | **0 errors** across `googlemaps/` and `tests/` |
| Format (`ruff format`)      | **clean** |
| Python 2 compatibility code | **removed** (modern Python 3.8+ only) |
| Packaging                   | **PEP 621** via `pyproject.toml`; `setup.py` is a 3-line shim |
| String formatting           | **f-strings** throughout |
| Exception chaining          | `raise ... from err` everywhere |
| Type hints                  | New modules (`cache.py`, `batch.py`) are fully annotated |

Run `pytest -q` and `ruff check googlemaps tests` locally to verify.

---

## Documentation & resources

[Documentation for the `google-maps-services-python` library](https://googlemaps.github.io/google-maps-services-python/docs/index.html)

### Getting started
- [Get Started with Google Maps Platform](https://developers.google.com/maps/gmp-get-started)
- [Generating/restricting an API key](https://developers.google.com/maps/gmp-get-started#api-key)
- [Authenticating with a client ID](https://developers.google.com/maps/documentation/directions/get-api-key#client-id)

### API docs
- [Google Maps Platform web services](https://developers.google.com/maps/apis-by-platform#web_service_apis)
- [Directions API](https://developers.google.com/maps/documentation/directions/)
- [Distance Matrix API](https://developers.google.com/maps/documentation/distancematrix/)
- [Elevation API](https://developers.google.com/maps/documentation/elevation/)
- [Geocoding API](https://developers.google.com/maps/documentation/geocoding/)
- [Geolocation API](https://developers.google.com/maps/documentation/geolocation/)
- [Time Zone API](https://developers.google.com/maps/documentation/timezone/)
- [Roads API](https://developers.google.com/maps/documentation/roads/)
- [Places API](https://developers.google.com/maps/documentation/places/)
- [Maps Static API](https://developers.google.com/maps/documentation/maps-static/)

## Support

This library is community supported. The fork additions
([googlemaps/cache.py](googlemaps/cache.py) and
[googlemaps/batch.py](googlemaps/batch.py)) are covered by their own dedicated
test files. We're comfortable enough with the stability and features of the
library that you can build real production applications on it.

If you find a bug or have a feature suggestion, please log an issue.
If you'd like to contribute, please read [CONTRIB.md](CONTRIB.md).

- [Report an issue](https://github.com/googlemaps/google-maps-services-python/issues)
- [Contribute](https://github.com/googlemaps/google-maps-services-python/blob/master/CONTRIB.md)
- [StackOverflow](http://stackoverflow.com/questions/tagged/google-maps)
