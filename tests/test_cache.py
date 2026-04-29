#
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#

"""Tests for googlemaps.cache and Client cache integration."""

import threading

import pytest
import responses

import googlemaps
from googlemaps.cache import (
    _AUTH_PARAMS,
    BaseCache,
    CacheStats,
    InMemoryTTLCache,
    make_cache_key,
)

# --------------------------------------------------------------------------- #
# make_cache_key                                                              #
# --------------------------------------------------------------------------- #


class TestMakeCacheKey:
    def test_strips_auth_params(self):
        a = make_cache_key("/p", [("address", "Sydney"), ("key", "AIzaA")])
        b = make_cache_key("/p", [("address", "Sydney"), ("key", "AIzaB")])
        assert a == b

    def test_order_independent(self):
        a = make_cache_key("/p", [("a", 1), ("b", 2)])
        b = make_cache_key("/p", [("b", 2), ("a", 1)])
        assert a == b

    def test_path_matters(self):
        assert make_cache_key("/p1", []) != make_cache_key("/p2", [])

    def test_value_difference(self):
        a = make_cache_key("/p", [("q", "x")])
        b = make_cache_key("/p", [("q", "y")])
        assert a != b

    def test_all_auth_params_filtered(self):
        params = [(p, "v") for p in _AUTH_PARAMS] + [("q", "x")]
        key = make_cache_key("/p", params)
        assert key == ("/p", (("q", "x"),))

    def test_key_is_hashable(self):
        key = make_cache_key("/p", [("q", "x")])
        # Must be usable as a dict key.
        d = {key: 1}
        assert d[key] == 1


# --------------------------------------------------------------------------- #
# InMemoryTTLCache                                                            #
# --------------------------------------------------------------------------- #


class TestInMemoryTTLCache:
    def test_constructor_validates(self):
        with pytest.raises(ValueError):
            InMemoryTTLCache(maxsize=0)
        with pytest.raises(ValueError):
            InMemoryTTLCache(ttl=0)
        with pytest.raises(ValueError):
            InMemoryTTLCache(ttl=-5)

    def test_set_and_get(self):
        c = InMemoryTTLCache(maxsize=4, ttl=60)
        c.set("k", "v")
        assert c.get("k") == "v"
        assert len(c) == 1
        assert "k" in c

    def test_miss_returns_none(self):
        assert InMemoryTTLCache().get("absent") is None

    def test_ttl_expiration_with_fake_clock(self):
        c = InMemoryTTLCache(maxsize=4, ttl=10)
        clock = [1000.0]
        c._now = lambda: clock[0]
        c.set("k", "v")
        assert c.get("k") == "v"
        clock[0] += 5
        assert c.get("k") == "v"  # still alive
        clock[0] += 6  # past TTL
        assert c.get("k") is None
        stats = c.stats()
        assert stats.expirations == 1
        assert stats.hits == 2  # set + still-alive read; set doesn't count
        # Only get() increments hits/misses; recompute exactly:
        # 1 hit (still-alive) + 1 miss (expired). 'set' counts in stats.sets.
        assert stats.misses == 1
        assert stats.sets == 1

    def test_lru_eviction(self):
        c = InMemoryTTLCache(maxsize=2, ttl=None)
        c.set("a", 1)
        c.set("b", 2)
        c.get("a")  # promote a
        c.set("c", 3)  # should evict b
        assert c.get("a") == 1
        assert c.get("b") is None
        assert c.get("c") == 3
        assert c.stats().evictions == 1

    def test_set_overwrites_and_promotes(self):
        c = InMemoryTTLCache(maxsize=2, ttl=None)
        c.set("a", 1)
        c.set("b", 2)
        c.set("a", 99)  # overwrite + promote
        c.set("c", 3)  # evicts b, not a
        assert c.get("a") == 99
        assert c.get("b") is None

    def test_clear_resets_stats(self):
        c = InMemoryTTLCache()
        c.set("k", "v")
        c.get("k")
        c.get("missing")
        c.clear()
        s = c.stats()
        assert s.hits == s.misses == s.sets == s.evictions == s.expirations == 0
        assert len(c) == 0

    def test_stats_snapshot_is_copy(self):
        c = InMemoryTTLCache()
        c.set("k", "v")
        s1 = c.stats()
        c.set("k2", "v")
        assert s1.sets == 1  # snapshot, not live

    def test_hit_ratio(self):
        s = CacheStats(hits=3, misses=1)
        assert s.hit_ratio == 0.75
        assert CacheStats().hit_ratio == 0.0

    def test_thread_safety_under_contention(self):
        c = InMemoryTTLCache(maxsize=1000, ttl=None)
        N = 200

        def worker(start):
            for i in range(start, start + N):
                c.set(i, i * 2)
                assert c.get(i) == i * 2

        threads = [threading.Thread(target=worker, args=(i * N,)) for i in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert c.stats().sets == 8 * N

    def test_base_cache_is_abstract(self):
        b = BaseCache()
        with pytest.raises(NotImplementedError):
            b.get("x")
        with pytest.raises(NotImplementedError):
            b.set("x", 1)
        with pytest.raises(NotImplementedError):
            b.clear()
        with pytest.raises(NotImplementedError):
            b.stats()


# --------------------------------------------------------------------------- #
# Client integration                                                          #
# --------------------------------------------------------------------------- #


class TestClientCacheIntegration:
    @responses.activate
    def test_geocode_served_from_cache_on_second_call(self):
        responses.add(
            responses.GET,
            "https://maps.googleapis.com/maps/api/geocode/json",
            json={"status": "OK", "results": [{"formatted_address": "Sydney NSW"}]},
            status=200,
        )
        gmaps = googlemaps.Client(key="AIzaTEST")
        gmaps.cache = InMemoryTTLCache(maxsize=8, ttl=60)

        r1 = gmaps.geocode("Sydney")
        r2 = gmaps.geocode("Sydney")

        assert r1 == r2
        # Only ONE network call must have happened.
        assert len(responses.calls) == 1
        stats = gmaps.cache.stats()
        assert stats.hits == 1
        assert stats.sets == 1

    @responses.activate
    def test_different_query_misses_cache(self):
        responses.add(
            responses.GET,
            "https://maps.googleapis.com/maps/api/geocode/json",
            json={"status": "OK", "results": []},
            status=200,
        )
        gmaps = googlemaps.Client(key="AIzaTEST")
        gmaps.cache = InMemoryTTLCache()
        gmaps.geocode("Sydney")
        gmaps.geocode("Melbourne")
        assert len(responses.calls) == 2

    @responses.activate
    def test_post_request_is_not_cached(self):
        # geolocate uses POST.
        responses.add(
            responses.POST,
            "https://www.googleapis.com/geolocation/v1/geolocate",
            json={"location": {"lat": 1, "lng": 2}, "accuracy": 10},
            status=200,
        )
        gmaps = googlemaps.Client(key="AIzaTEST")
        gmaps.cache = InMemoryTTLCache()
        gmaps.geolocate()
        gmaps.geolocate()
        # Both calls hit the network; nothing was cached.
        assert len(responses.calls) == 2
        assert gmaps.cache.stats().sets == 0

    @responses.activate
    def test_no_cache_when_unset(self):
        responses.add(
            responses.GET,
            "https://maps.googleapis.com/maps/api/geocode/json",
            json={"status": "OK", "results": []},
            status=200,
        )
        gmaps = googlemaps.Client(key="AIzaTEST")
        # cache attribute exists and defaults to None.
        assert gmaps.cache is None
        gmaps.geocode("Sydney")
        gmaps.geocode("Sydney")
        assert len(responses.calls) == 2

    @responses.activate
    def test_cache_shared_across_credentials(self):
        responses.add(
            responses.GET,
            "https://maps.googleapis.com/maps/api/geocode/json",
            json={"status": "OK", "results": [{"formatted_address": "Sydney"}]},
            status=200,
        )
        cache = InMemoryTTLCache()
        c1 = googlemaps.Client(key="AIzaAAAA")
        c2 = googlemaps.Client(key="AIzaBBBB")
        c1.cache = c2.cache = cache
        c1.geocode("Sydney")
        c2.geocode("Sydney")  # same logical query, different key
        assert len(responses.calls) == 1
