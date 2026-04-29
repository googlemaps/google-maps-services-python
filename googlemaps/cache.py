#
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#

"""Pluggable response cache for the Google Maps client.

This module ships an opinionated, in-process TTL+LRU cache implementation
(:class:`InMemoryTTLCache`) and a tiny abstract interface (:class:`BaseCache`)
that any external backend (Redis, memcached, disk) can implement.

When a cache is attached to a :class:`googlemaps.Client` instance via
``client.cache = InMemoryTTLCache(...)``, idempotent ``GET`` requests are
served from the cache when their ``(path, params)`` pair has been seen within
the TTL. ``POST`` requests and responses with non-``OK``/``ZERO_RESULTS`` API
status are never cached.

The cache key intentionally **excludes** authentication parameters
(``key``, ``client``, ``signature``, ``channel``) so the same lookup is
shareable across credentials and reproducible in tests.

Example
-------

.. code-block:: python

    import googlemaps
    from googlemaps.cache import InMemoryTTLCache

    gmaps = googlemaps.Client(key="AIza...")
    gmaps.cache = InMemoryTTLCache(maxsize=512, ttl=300)  # 5 min TTL

    gmaps.geocode("Sydney")  # network call
    gmaps.geocode("Sydney")  # served from cache
    print(gmaps.cache.stats())  # CacheStats(hits=1, misses=1, ...)
"""

from __future__ import annotations

import threading
import time
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any, Iterable

# Parameters that should never participate in the cache key. Including them
# would defeat sharing across credentials and leak secrets into key dumps.
_AUTH_PARAMS = frozenset({"key", "client", "signature", "channel"})


def make_cache_key(path: str, params: Iterable[tuple[str, Any]]) -> tuple:
    """Build a deterministic, hashable cache key from a request.

    :param path: Request path (e.g. ``"/maps/api/geocode/json"``).
    :param params: Request parameters as an iterable of ``(key, value)`` tuples
        (the same shape used internally by :meth:`Client._generate_auth_url`).
    :returns: A hashable tuple suitable for use as a dict key.
    """
    filtered = tuple(sorted((k, v) for k, v in params if k not in _AUTH_PARAMS))
    return (path, filtered)


@dataclass
class CacheStats:
    """Lightweight counters for cache observability."""

    hits: int = 0
    misses: int = 0
    evictions: int = 0
    expirations: int = 0
    sets: int = 0

    @property
    def hit_ratio(self) -> float:
        total = self.hits + self.misses
        return (self.hits / total) if total else 0.0


class BaseCache:
    """Abstract cache interface.

    Implementations must be safe for concurrent use from multiple threads.
    """

    def get(self, key) -> Any | None:  # pragma: no cover - interface
        raise NotImplementedError

    def set(self, key, value) -> None:  # pragma: no cover - interface
        raise NotImplementedError

    def clear(self) -> None:  # pragma: no cover - interface
        raise NotImplementedError

    def stats(self) -> CacheStats:  # pragma: no cover - interface
        raise NotImplementedError


@dataclass
class _Entry:
    value: Any
    expires_at: float


class InMemoryTTLCache(BaseCache):
    """Thread-safe in-memory cache with TTL eviction and LRU bound.

    :param maxsize: Maximum number of entries. When exceeded the
        least-recently-used entry is evicted. Must be ``>= 1``.
    :param ttl: Seconds an entry remains valid after insertion. ``None``
        disables TTL (entries live until evicted).
    """

    def __init__(self, maxsize: int = 256, ttl: float | None = 300) -> None:
        if maxsize < 1:
            raise ValueError("maxsize must be >= 1")
        if ttl is not None and ttl <= 0:
            raise ValueError("ttl must be > 0 or None")
        self._maxsize = maxsize
        self._ttl = ttl
        self._data: OrderedDict[Any, _Entry] = OrderedDict()
        self._lock = threading.RLock()
        self._stats = CacheStats()
        # Injectable clock for testability.
        self._now = time.monotonic

    # ------------------------------------------------------------------ API

    def get(self, key) -> Any | None:
        with self._lock:
            entry = self._data.get(key)
            if entry is None:
                self._stats.misses += 1
                return None
            if entry.expires_at and entry.expires_at <= self._now():
                # Expired — drop and miss.
                del self._data[key]
                self._stats.expirations += 1
                self._stats.misses += 1
                return None
            # LRU touch.
            self._data.move_to_end(key)
            self._stats.hits += 1
            return entry.value

    def set(self, key, value) -> None:
        with self._lock:
            expires_at = self._now() + self._ttl if self._ttl else 0.0
            if key in self._data:
                self._data.move_to_end(key)
            self._data[key] = _Entry(value=value, expires_at=expires_at)
            self._stats.sets += 1
            while len(self._data) > self._maxsize:
                self._data.popitem(last=False)
                self._stats.evictions += 1

    def clear(self) -> None:
        with self._lock:
            self._data.clear()
            self._stats = CacheStats()

    def stats(self) -> CacheStats:
        with self._lock:
            # Return a snapshot to avoid races from the caller.
            return CacheStats(
                hits=self._stats.hits,
                misses=self._stats.misses,
                evictions=self._stats.evictions,
                expirations=self._stats.expirations,
                sets=self._stats.sets,
            )

    # ----------------------------------------------------------- introspection

    def __len__(self) -> int:
        with self._lock:
            return len(self._data)

    def __contains__(self, key) -> bool:
        return self.get(key) is not None
