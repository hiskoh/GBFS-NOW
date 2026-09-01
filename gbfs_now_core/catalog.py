# -*- coding: utf-8 -*-

import csv
from io import StringIO
import threading

from .client import DEFAULT_TIMEOUT_SECONDS, GbfsClient, GbfsClientError


SYSTEMS_CSV_URL = "https://raw.githubusercontent.com/MobilityData/gbfs/master/systems.csv"

FALLBACK_HEADERS = [
    "Country Code",
    "Name",
    "Location",
    "System ID",
    "URL",
    "Auto-Discovery URL",
    "Supported Versions",
    "Authentication Info URL",
    "Authentication Type",
    "Authentication Parameter Name",
]


class CatalogError(RuntimeError):
    pass


_CACHE = None
_CACHE_ERROR = None
_LOADING = False
_LOCK = threading.Lock()
_READY = threading.Event()


def fetch_systems_catalog(timeout=DEFAULT_TIMEOUT_SECONDS):
    cached = _cached_catalog()
    if cached is not None:
        return cached

    if _is_loading():
        _READY.wait(timeout)
        cached = _cached_catalog()
        if cached is not None:
            return cached

    return _download_and_store(timeout)


def prefetch_systems_catalog(timeout=DEFAULT_TIMEOUT_SECONDS):
    global _CACHE_ERROR, _LOADING
    with _LOCK:
        if _CACHE is not None or _LOADING:
            return
        _CACHE_ERROR = None
        _LOADING = True
        _READY.clear()

    thread = threading.Thread(
        target=_prefetch_worker,
        args=(timeout,),
        name="GBFS-NOW catalog prefetch",
        daemon=True,
    )
    thread.start()


def _prefetch_worker(timeout):
    try:
        _download_and_store(timeout)
    except CatalogError:
        pass


def _download_and_store(timeout):
    global _CACHE, _CACHE_ERROR, _LOADING
    try:
        catalog = _download_systems_catalog(timeout)
    except CatalogError as error:
        with _LOCK:
            _CACHE_ERROR = error
            _LOADING = False
            _READY.set()
        raise

    with _LOCK:
        _CACHE = catalog
        _CACHE_ERROR = None
        _LOADING = False
        _READY.set()
    return _clone_catalog(catalog)


def _download_systems_catalog(timeout):
    try:
        text = GbfsClient(timeout).get_text(SYSTEMS_CSV_URL)
    except GbfsClientError as error:
        raise CatalogError(str(error)) from error

    reader = csv.DictReader(StringIO(text), skipinitialspace=True)
    headers = reader.fieldnames or FALLBACK_HEADERS
    rows = [[row.get(header, "") for header in headers] for row in reader]
    return headers, rows


def _cached_catalog():
    with _LOCK:
        if _CACHE is None:
            return None
        return _clone_catalog(_CACHE)


def _clone_catalog(catalog):
    headers, rows = catalog
    return list(headers), [list(row) for row in rows]


def _is_loading():
    with _LOCK:
        return _LOADING
