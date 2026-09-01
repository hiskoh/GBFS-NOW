# -*- coding: utf-8 -*-

import datetime
from dataclasses import dataclass


DEFAULT_LANGUAGE = "default"

FEED_ALIASES = {
    "free_bike_status": ("free_bike_status", "vehicle_status"),
    "vehicle_status": ("vehicle_status", "free_bike_status"),
}


class GbfsDataError(ValueError):
    pass


@dataclass
class Discovery:
    source_url: str
    raw: dict
    system_information: dict = None

    @property
    def version(self):
        return feed_version(self.raw)

    @property
    def is_flat(self):
        return is_flat_discovery(self.raw)

    @property
    def languages(self):
        return feed_languages(self.raw, self.system_information)

    def feeds(self, language=None):
        return feeds_for_language(self.raw, language)

    def feed_url(self, feed_name, language=None):
        return feed_url(self.raw, feed_name, language)

    def default_language(self):
        languages = self.languages
        return languages[0] if languages else DEFAULT_LANGUAGE


def feed_version(gbfs_json):
    if isinstance(gbfs_json, dict) and gbfs_json.get("version") is not None:
        return str(gbfs_json["version"])
    return "1.0"


def payload_data(feed_json):
    if isinstance(feed_json, dict) and isinstance(feed_json.get("data"), dict):
        return feed_json["data"]
    return {}


def is_flat_discovery(gbfs_json):
    data = payload_data(gbfs_json)
    return isinstance(data.get("feeds"), list)


def feed_languages(gbfs_json, system_information=None):
    data = payload_data(gbfs_json)

    if is_flat_discovery(gbfs_json):
        system_data = payload_data(system_information)
        languages = system_data.get("languages")
        if isinstance(languages, list) and languages:
            return [str(language) for language in languages]
        return [DEFAULT_LANGUAGE]

    languages = []
    for language, value in data.items():
        if isinstance(value, dict) and isinstance(value.get("feeds"), list):
            languages.append(str(language))

    return languages or [DEFAULT_LANGUAGE]


def feeds_for_language(gbfs_json, language=None):
    data = payload_data(gbfs_json)

    if isinstance(data.get("feeds"), list):
        return data["feeds"]

    if language and isinstance(data.get(language), dict):
        feeds = data[language].get("feeds")
        if isinstance(feeds, list):
            return feeds

    for value in data.values():
        if isinstance(value, dict) and isinstance(value.get("feeds"), list):
            return value["feeds"]

    return []


def feed_url(gbfs_json, feed_name, language=None):
    aliases = FEED_ALIASES.get(feed_name, (feed_name,))

    for name in aliases:
        for feed in feeds_for_language(gbfs_json, language):
            if isinstance(feed, dict) and feed.get("name") == name:
                return feed.get("url")

    return None


def localized_text(value, language=None):
    if not isinstance(value, list):
        return None

    localized_items = [
        item for item in value if isinstance(item, dict) and "text" in item
    ]
    if not localized_items:
        return None

    if language and language != DEFAULT_LANGUAGE:
        language_lower = language.lower()
        language_root = language_lower.split("-", 1)[0]
        for item in localized_items:
            item_language = str(item.get("language", "")).lower()
            if item_language == language_lower:
                return item.get("text")
        for item in localized_items:
            item_language = str(item.get("language", "")).lower()
            if item_language.split("-", 1)[0] == language_root:
                return item.get("text")

    return localized_items[0].get("text")


def display_value(value, language=None):
    text = localized_text(value, language)
    if text is not None:
        return text

    if value is None:
        return None

    if isinstance(value, list):
        values = [display_value(item, language) for item in value]
        values = [str(item) for item in values if item is not None]
        separator = "\n" if any("\n" in item for item in values) else ", "
        return separator.join(values)

    if isinstance(value, dict):
        if "text" in value:
            return value.get("text")
        if "count" in value and (
            "vehicle_type_id" in value or "vehicle_type_ids" in value
        ):
            vehicle_type = value.get("vehicle_type_id", value.get("vehicle_type_ids"))
            if isinstance(vehicle_type, list):
                vehicle_type = ", ".join(display_text(item, language) for item in vehicle_type)
            return "{}: {}".format(vehicle_type, value.get("count"))
        return "\n".join(
            "{}: {}".format(key, display_value(item, language))
            for key, item in value.items()
            if item is not None
        )

    return value


def display_text(value, language=None):
    value = display_value(value, language)
    return "" if value is None else str(value)


def field_value(item, key, language=None, fallback_keys=None):
    keys = [key] + list(fallback_keys or [])
    for candidate in keys:
        value, found = nested_value(item, candidate)
        if found:
            return display_value(value, language)
    return None


def nested_value(item, key):
    value = item
    for part in key.split("."):
        if not isinstance(value, dict) or part not in value:
            return None, False
        value = value[part]
    return value, True


def records(feed_json, *keys):
    data = payload_data(feed_json)
    for key in keys:
        value = data.get(key)
        if isinstance(value, list):
            return value
    return []


def as_float(value):
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def format_timestamp(value):
    if value is None:
        return None

    if isinstance(value, (int, float)):
        return datetime.datetime.fromtimestamp(
            value, datetime.timezone.utc
        ).isoformat()

    if isinstance(value, str):
        stripped = value.strip()
        if stripped.isdigit():
            return format_timestamp(int(stripped))
        return stripped

    return str(value)
