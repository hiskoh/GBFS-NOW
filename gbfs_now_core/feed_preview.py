# -*- coding: utf-8 -*-

import datetime
from dataclasses import dataclass

from . import compat


LAYER_FEEDS = [
    ("Stations", "station_information", ("stations",)),
    ("Station status", "station_status", ("stations",)),
    ("Vehicles", "vehicle_status", ("vehicles", "bikes")),
]


@dataclass
class FeedPreview:
    layer_name: str
    feed_name: str
    url: str = None
    record_count: int = None
    last_updated: str = ""
    ttl: str = ""
    age: str = ""
    error: str = ""
    ttl_seconds: int = None
    age_seconds: int = None

    @property
    def available(self):
        return bool(self.url) and not self.error

    @property
    def is_stale(self):
        if self.ttl_seconds is None or self.ttl_seconds <= 0:
            return False
        if self.age_seconds is None:
            return False
        return self.age_seconds > self.ttl_seconds


def summarize_feed(layer_name, feed_name, record_keys, url=None, feed_json=None, error=None):
    if not url:
        return FeedPreview(layer_name, feed_name, error="Feed not published")

    if error:
        return FeedPreview(layer_name, feed_name, url=url, error=str(error))

    feed_json = feed_json or {}
    ttl_seconds = _ttl_seconds(feed_json.get("ttl"))
    age_seconds = _age_seconds(feed_json.get("last_updated"))
    return FeedPreview(
        layer_name=layer_name,
        feed_name=feed_name,
        url=url,
        record_count=len(compat.records(feed_json, *record_keys)),
        last_updated=compat.format_timestamp(feed_json.get("last_updated")),
        ttl=_format_duration(ttl_seconds) if ttl_seconds is not None else "",
        age=_format_age_seconds(age_seconds),
        ttl_seconds=ttl_seconds,
        age_seconds=age_seconds,
    )


def layer_preview_rows(previews, include_station_status=False):
    rows = []
    for preview in previews:
        status = "Will create" if preview.available else preview.error
        if preview.is_stale and preview.available:
            status = "Stale, will create"
        if preview.feed_name == "station_status" and preview.available and not include_station_status:
            status = "Available, not selected"
            if preview.is_stale:
                status = "Stale, not selected"
        rows.append(
            [
                "{} ({})".format(preview.layer_name, preview.feed_name),
                "" if preview.record_count is None else str(preview.record_count),
                preview.last_updated,
                preview.ttl,
                preview.age,
                status,
            ]
        )
    return rows


def _format_ttl(value):
    seconds = _ttl_seconds(value)
    if seconds is None:
        return ""
    return _format_duration(seconds)


def _ttl_seconds(value):
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def format_age(value, now=None):
    seconds = _age_seconds(value, now)
    return _format_age_seconds(seconds)


def _age_seconds(value, now=None):
    timestamp = _parse_timestamp(value)
    if timestamp is None:
        return None
    now = now or datetime.datetime.now(datetime.timezone.utc)
    return int((now - timestamp).total_seconds())


def _format_age_seconds(seconds):
    if seconds is None:
        return ""
    if seconds < 0:
        return "in {}".format(_format_duration(abs(seconds)))
    return "{} ago".format(_format_duration(seconds))


def _parse_timestamp(value):
    if value is None or value == "":
        return None

    if isinstance(value, (int, float)):
        return datetime.datetime.fromtimestamp(value, datetime.timezone.utc)

    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return None
        if stripped.isdigit():
            return _parse_timestamp(int(stripped))
        try:
            timestamp = datetime.datetime.fromisoformat(stripped.replace("Z", "+00:00"))
        except ValueError:
            return None
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=datetime.timezone.utc)
        return timestamp.astimezone(datetime.timezone.utc)

    return None


def _format_duration(seconds):
    if seconds < 60:
        return "{}s".format(seconds)
    minutes = seconds // 60
    if minutes < 60:
        return "{}m".format(minutes)
    hours = minutes // 60
    if hours < 48:
        return "{}h".format(hours)
    days = hours // 24
    return "{}d".format(days)
