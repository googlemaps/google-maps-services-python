"""Advanced parametrized tests for googlemaps.cache."""

from __future__ import annotations

import threading
import time

import pytest

from googlemaps.cache import (
    _AUTH_PARAMS,
    BaseCache,
    CacheStats,
    InMemoryTTLCache,
    make_cache_key,
)

# ---------------------------------------------------------------------------
# make_cache_key
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("auth_param", sorted(_AUTH_PARAMS))
def test_make_cache_key_strips_each_auth_param(auth_param):
    base = [("address", "Sydney")]
    with_auth = [*base, (auth_param, "secret")]
    assert make_cache_key("/p", base) == make_cache_key("/p", with_auth)


@pytest.mark.parametrize(
    "params_a,params_b",
    [
        ([("a", "1"), ("b", "2")], [("b", "2"), ("a", "1")]),
        ([("x", "y"), ("z", "w")], [("z", "w"), ("x", "y")]),
        ([("a", "1")], [("a", "1")]),
        ([], []),
    ],
)
def test_make_cache_key_order_independent(params_a, params_b):
    assert make_cache_key("/p", params_a) == make_cache_key("/p", params_b)


@pytest.mark.parametrize(
    "path_a,path_b",
    [("/a", "/b"), ("/maps/api/geocode/json", "/maps/api/places/json"), ("", "/")],
)
def test_make_cache_key_path_matters(path_a, path_b):
    assert make_cache_key(path_a, []) != make_cache_key(path_b, [])


def test_make_cache_key_is_hashable():
    key = make_cache_key("/p", [("a", "1"), ("key", "secret")])
    d = {key: "value"}  # would raise TypeError if not hashable
    assert d[key] == "value"
    assert hash(key) == hash(key)


@pytest.mark.parametrize(
    "params,expected_filtered",
    [
        ([("key", "K")], ()),
        ([("address", "Sydney"), ("key", "K")], (("address", "Sydney"),)),
        ([("client", "C"), ("signature", "S"), ("channel", "CH")], ()),
        (
            [("a", 1), ("b", 2), ("key", "K")],
            (("a", 1), ("b", 2)),
        ),
    ],
)
def test_make_cache_key_filtered_content(params, expected_filtered):
    _, filtered = make_cache_key("/p", params)
    assert filtered == expected_filtered


# ---------------------------------------------------------------------------
# BaseCache abstract behaviour
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("method,args", [
    ("get", ("k",)),
    ("set", ("k", "v")),
    ("clear", ()),
    ("stats", ()),
])
def test_base_cache_methods_raise(method, args):
    with pytest.raises(NotImplementedError):
        getattr(BaseCache(), method)(*args)


# ---------------------------------------------------------------------------
# CacheStats
# ---------------------------------------------------------------------------

def test_cache_stats_defaults_zero():
    s = CacheStats()
    assert s.hits == s.misses == s.evictions == s.expirations == s.sets == 0
    assert s.hit_ratio == 0.0


@pytest.mark.parametrize(
    "hits,misses,expected",
    [
        (0, 0, 0.0),
        (1, 0, 1.0),
        (0, 1, 0.0),
        (3, 1, 0.75),
        (1, 3, 0.25),
        (50, 50, 0.5),
        (100, 0, 1.0),
        (0, 100, 0.0),
    ],
)
def test_cache_stats_hit_ratio(hits, misses, expected):
    s = CacheStats(hits=hits, misses=misses)
    assert s.hit_ratio == pytest.approx(expected)


# ---------------------------------------------------------------------------
# InMemoryTTLCache — construction
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("bad_size", [0, -1, -100])
def test_cache_rejects_bad_maxsize(bad_size):
    with pytest.raises(ValueError):
        InMemoryTTLCache(maxsize=bad_size)


@pytest.mark.parametrize("bad_ttl", [0, -1, -0.5])
def test_cache_rejects_bad_ttl(bad_ttl):
    with pytest.raises(ValueError):
        InMemoryTTLCache(ttl=bad_ttl)


@pytest.mark.parametrize("ok_size", [1, 2, 100, 10_000])
def test_cache_accepts_valid_maxsize(ok_size):
    InMemoryTTLCache(maxsize=ok_size)


@pytest.mark.parametrize("ok_ttl", [None, 0.001, 1, 60, 3600])
def test_cache_accepts_valid_ttl(ok_ttl):
    InMemoryTTLCache(ttl=ok_ttl)


# ---------------------------------------------------------------------------
# InMemoryTTLCache — basic get/set/miss
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "key,value",
    [
        ("simple", "string"),
        (("tuple", "key"), {"a": 1}),
        ((1, 2, 3), [1, 2, 3]),
        (("nested", ("a", "b")), {"deeply": {"nested": "value"}}),
        ((), 0),
        (("empty",), ""),
    ],
)
def test_cache_set_then_get(key, value):
    c = InMemoryTTLCache(maxsize=10)
    c.set(key, value)
    assert c.get(key) == value


def test_cache_miss_returns_none():
    c = InMemoryTTLCache()
    assert c.get(("missing",)) is None


def test_cache_overwrite_keeps_size():
    c = InMemoryTTLCache(maxsize=10)
    for _ in range(5):
        c.set("k", "v")
    assert len(c) == 1


def test_cache_len_grows_with_unique_sets():
    c = InMemoryTTLCache(maxsize=100)
    for i in range(50):
        c.set(("k", i), i)
    assert len(c) == 50


@pytest.mark.parametrize("n", [2, 5, 10, 50])
def test_cache_lru_eviction_count(n):
    c = InMemoryTTLCache(maxsize=n)
    for i in range(n * 3):
        c.set(("k", i), i)
    assert len(c) == n
    assert c.stats().evictions == n * 2


def test_cache_lru_evicts_oldest_first():
    c = InMemoryTTLCache(maxsize=3)
    c.set("a", 1)
    c.set("b", 2)
    c.set("c", 3)
    c.set("d", 4)  # evicts "a"
    assert c.get("a") is None
    assert c.get("b") == 2
    assert c.get("c") == 3
    assert c.get("d") == 4


def test_cache_lru_get_promotes_recency():
    c = InMemoryTTLCache(maxsize=3)
    c.set("a", 1)
    c.set("b", 2)
    c.set("c", 3)
    c.get("a")  # promote
    c.set("d", 4)  # should now evict "b"
    assert c.get("b") is None
    assert c.get("a") == 1


# ---------------------------------------------------------------------------
# TTL behaviour with injectable clock
# ---------------------------------------------------------------------------

class _FakeClock:
    def __init__(self, start: float = 1000.0) -> None:
        self.t = start

    def __call__(self) -> float:
        return self.t

    def advance(self, dt: float) -> None:
        self.t += dt


@pytest.mark.parametrize("ttl", [0.5, 1, 5, 60])
def test_cache_ttl_expiration(ttl):
    clock = _FakeClock()
    c = InMemoryTTLCache(maxsize=10, ttl=ttl)
    c._now = clock
    c.set("k", "v")
    assert c.get("k") == "v"
    clock.advance(ttl + 0.01)
    assert c.get("k") is None
    assert c.stats().expirations == 1


def test_cache_ttl_none_never_expires():
    clock = _FakeClock()
    c = InMemoryTTLCache(maxsize=10, ttl=None)
    c._now = clock
    c.set("k", "v")
    clock.advance(1_000_000)
    assert c.get("k") == "v"


def test_cache_ttl_partial_age_still_valid():
    clock = _FakeClock()
    c = InMemoryTTLCache(maxsize=10, ttl=10)
    c._now = clock
    c.set("k", "v")
    clock.advance(5)
    assert c.get("k") == "v"


# ---------------------------------------------------------------------------
# stats / contains / clear
# ---------------------------------------------------------------------------

def test_cache_stats_snapshot_isolation():
    c = InMemoryTTLCache()
    c.set("a", 1)
    snap = c.stats()
    c.set("b", 2)
    assert snap.sets == 1  # not mutated by subsequent activity


def test_cache_clear_resets_data_and_stats():
    c = InMemoryTTLCache(maxsize=10)
    for i in range(5):
        c.set(("k", i), i)
    c.get(("k", 0))
    c.get(("missing",))
    c.clear()
    assert len(c) == 0
    s = c.stats()
    assert s.hits == s.misses == s.sets == 0


def test_cache_contains_uses_get_path():
    c = InMemoryTTLCache(maxsize=10)
    c.set("k", "v")
    assert "k" in c
    assert "missing" not in c
    s = c.stats()
    assert s.hits >= 1
    assert s.misses >= 1


@pytest.mark.parametrize("count", [10, 50, 200])
def test_cache_set_counter(count):
    c = InMemoryTTLCache(maxsize=count)
    for i in range(count):
        c.set(("k", i), i)
    assert c.stats().sets == count


# ---------------------------------------------------------------------------
# Concurrency
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("n_threads,iters", [(2, 100), (4, 200), (8, 100)])
def test_cache_thread_safety(n_threads, iters):
    c = InMemoryTTLCache(maxsize=1000)
    barrier = threading.Barrier(n_threads)

    def worker(tid):
        barrier.wait()
        for i in range(iters):
            c.set((tid, i), i)
            c.get((tid, i))

    threads = [threading.Thread(target=worker, args=(t,)) for t in range(n_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    s = c.stats()
    assert s.sets == n_threads * iters
    assert s.hits == n_threads * iters


def test_cache_concurrent_overwrite_no_corruption():
    c = InMemoryTTLCache(maxsize=10)

    def worker():
        for _ in range(500):
            c.set("k", "v")

    threads = [threading.Thread(target=worker) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert c.get("k") == "v"
    assert len(c) == 1


# ---------------------------------------------------------------------------
# Real-time TTL sanity (small TTL on the real clock)
# ---------------------------------------------------------------------------

def test_cache_real_clock_ttl_short():
    c = InMemoryTTLCache(maxsize=2, ttl=0.05)
    c.set("k", "v")
    assert c.get("k") == "v"
    time.sleep(0.1)
    assert c.get("k") is None
