#
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#

"""Concurrent batch helpers for the Google Maps client.

The official Google Maps web services are synchronous — one HTTP request per
call. When you need to geocode hundreds of addresses or fetch directions
between many origin/destination pairs, doing them serially is the bottleneck.

This module provides :class:`BatchExecutor`, a thin :class:`ThreadPoolExecutor`
wrapper that:

1. Respects the parent client's QPS quota (each worker still hits the same
   :class:`~googlemaps.client.Client` rate limiter).
2. Returns results in the **same order** as the inputs.
3. Captures per-item exceptions instead of cancelling the whole batch
   (``return_exceptions=True``, default), so one bad address does not
   poison the batch.
4. Supports any client method by name — including custom ones registered
   on the client.

Example
-------

.. code-block:: python

    import googlemaps
    from googlemaps.batch import BatchExecutor

    gmaps = googlemaps.Client(key="AIza...")
    batch = BatchExecutor(gmaps, max_workers=8)

    results = batch.run(
        "geocode",
        ["Sydney", "Melbourne", "Perth", "Bad address #@$"],
    )
    for query, result in zip(inputs, results):
        if isinstance(result, Exception):
            print(f"FAILED {query}: {result}")
        else:
            print(query, "->", result[0]["formatted_address"])

    # Convenience shortcuts:
    batch.geocode(["Sydney", "Melbourne"])
    batch.directions([("A", "B"), ("C", "D")])
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Iterable, Sequence


class BatchExecutor:
    """Run a Google Maps client method concurrently over a list of inputs.

    :param client: A :class:`googlemaps.Client` instance.
    :param max_workers: Worker thread count. Defaults to the smaller of
        ``client.queries_quota`` and ``32``.
    :param return_exceptions: When ``True`` (default) a failing item is
        returned as the raised :class:`Exception` instance instead of
        propagating. When ``False`` the first failure raises.
    """

    def __init__(
        self,
        client,
        max_workers: int | None = None,
        return_exceptions: bool = True,
    ) -> None:
        if client is None:
            raise ValueError("client is required")
        if max_workers is not None and max_workers < 1:
            raise ValueError("max_workers must be >= 1")
        self.client = client
        self.return_exceptions = return_exceptions
        if max_workers is None:
            quota = getattr(client, "queries_quota", 32) or 32
            max_workers = min(int(quota), 32)
        self.max_workers = max_workers

    # ------------------------------------------------------------------ core

    def run(
        self,
        method: str | Callable,
        inputs: Sequence[Any],
        *,
        common_kwargs: dict | None = None,
        unpack: bool = False,
    ) -> list:
        """Execute ``method`` once per item in ``inputs`` concurrently.

        :param method: Either the name of a method bound to ``client``
            (e.g. ``"geocode"``) or a callable taking ``(client, item, **kwargs)``.
        :param inputs: Iterable of items. Each item is passed positionally to
            the method (or unpacked when ``unpack=True``).
        :param common_kwargs: Optional keyword arguments forwarded to every
            invocation (e.g. ``{"language": "en"}``).
        :param unpack: When ``True`` and an item is a tuple/list, it is
            unpacked as positional arguments — useful for paired inputs like
            ``[(origin, destination), ...]`` for ``directions``.
        :returns: A list of results in the same order as ``inputs``.
        """
        if isinstance(method, str):
            fn = getattr(self.client, method, None)
            if fn is None or not callable(fn):
                raise AttributeError(f"client has no callable method {method!r}")
        else:
            fn = method

        common_kwargs = common_kwargs or {}
        items = list(inputs)

        def _call(item):
            args = tuple(item) if (unpack and isinstance(item, (tuple, list))) else (item,)
            return fn(*args, **common_kwargs)

        if not items:
            return []

        with ThreadPoolExecutor(max_workers=self.max_workers) as pool:
            futures = [pool.submit(_call, it) for it in items]
            results: list = []
            for fut in futures:
                try:
                    results.append(fut.result())
                except Exception as exc:
                    if not self.return_exceptions:
                        raise
                    results.append(exc)
            return results

    # -------------------------------------------------------------- shortcuts

    def geocode(self, addresses: Iterable[str], **kwargs) -> list:
        """Batch geocoding shortcut. Equivalent to ``run("geocode", addresses)``."""
        return self.run("geocode", list(addresses), common_kwargs=kwargs)

    def reverse_geocode(self, latlngs: Iterable, **kwargs) -> list:
        """Batch reverse-geocoding shortcut."""
        return self.run("reverse_geocode", list(latlngs), common_kwargs=kwargs)

    def directions(self, pairs: Iterable, **kwargs) -> list:
        """Batch directions shortcut.

        Each item in ``pairs`` must be a ``(origin, destination)`` tuple.
        """
        return self.run("directions", list(pairs), common_kwargs=kwargs, unpack=True)

    def place(self, place_ids: Iterable[str], **kwargs) -> list:
        """Batch place-details shortcut."""
        return self.run("place", list(place_ids), common_kwargs=kwargs)
