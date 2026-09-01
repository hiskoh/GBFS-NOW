# -*- coding: utf-8 -*-

import os
import xml.etree.ElementTree as ET
from functools import lru_cache

try:
    from qgis.PyQt.QtCore import QCoreApplication
except ImportError:
    QCoreApplication = None


EN = "en"
JA = "ja"
CONTEXT = "gbfs_now"

SOURCES = {
    "add_to_map": "Add to Map",
    "added_favorite": "Added to favorites.",
    "available": "Available",
    "catalog_source": "MobilityData GBFS systems catalog",
    "catalog_title": "GBFS Catalog",
    "catalog_tooltip": "Open GBFS catalog",
    "catalog_load_error": "Unable to load GBFS catalog: {error}",
    "collapse_service": "Collapse service information",
    "collapse_vehicle": "Collapse vehicle information",
    "data_format_label": "Data Format:",
    "data_format_value": "GBFS v{version}",
    "data_not_loaded": "Data not loaded",
    "data_language": "Data language",
    "default_language": "default",
    "duration_days": "{count}d",
    "duration_hours": "{count}h",
    "duration_minutes": "{count}m",
    "duration_seconds": "{count}s",
    "expand_service": "Expand service information",
    "expand_vehicle": "Expand vehicle information",
    "favorite_tooltip": "Favorites",
    "feed_error": "Feed error",
    "feed_error_short": "Feed error",
    "feed_missing": "Feed not published",
    "feed_station_information": "Station Information",
    "feed_station_status": "Station Status",
    "feed_vehicle_status": "Vehicle Status",
    "feeds_section": "3. Downloadable Information",
    "gbfs_url": "GBFS URL",
    "japanese_field_names": "Use Japanese field aliases when available",
    "language_label": "Language:",
    "language_section": "2. Language",
    "layers_added": "Added {count} layer(s) to the map.",
    "load_error": "Unable to load GBFS: {error}",
    "load_gbfs": "Load",
    "loaded": "GBFS v{version} / {mode} / {count} feed(s) ready",
    "mode_flat": "single feed list",
    "mode_language": "language feeds",
    "no_favorites": "No saved favorites",
    "no_layers_selected": "Select at least one available feed.",
    "operator_label": "Operator:",
    "plugin_title": "GBFS-NOW",
    "records": "Records",
    "refresh_error": "Unable to refresh feed preview: {error}",
    "remove_favorite": "Remove Favorite",
    "removed_favorite": "Removed from favorites.",
    "render_error": "Unable to render GBFS layers: {error}",
    "save_current_url": "Save Current URL",
    "search_label": "Search",
    "search_catalog_placeholder": "Search by city, system, country, or version",
    "select_gbfs_system": "Select a GBFS system",
    "select_language_first": "Select a language first",
    "service_section": "4. Service Information",
    "source_section": "1. Source",
    "stale": "Stale",
    "station_count": "{count} stations",
    "status_value": "Status {value}",
    "system_label": "System:",
    "system_type_label": "System Type:",
    "service_start_label": "Service Start Date:",
    "service_url_label": "Service URL:",
    "android_store_label": "Android Store:",
    "ios_store_label": "iOS Store:",
    "system_type_station": "Station-based system",
    "system_type_dockless": "Dockless system",
    "system_type_unknown": "Unknown",
    "ttl_value": "TTL {value}",
    "unknown_value": "-",
    "updated_ago": "Updated {value} ago",
    "updated_value": "Updated {value}",
    "url_label": "URL:",
    "url_required": "GBFS auto-discovery URL is required.",
    "vehicle_count": "{count} vehicles",
    "vehicle_info_empty": "No vehicle information",
    "vehicle_info_section": "5. Vehicle Information",
    "vehicle_meta": "{type_id} / {form_factor} / {propulsion_type}",
}


def language_for_locale(locale):
    return JA if str(locale or "").lower().startswith("ja") else EN


def text(key, language=EN, **values):
    source = SOURCES.get(key, key)
    template = translate(source, language)
    return template.format(**values)


def format_updated_age(age_seconds, language=EN):
    if age_seconds is None:
        return ""
    return text("updated_ago", language, value=format_duration(age_seconds, language))


def format_duration(seconds, language=EN):
    seconds = max(0, int(seconds))
    if seconds < 60:
        return text("duration_seconds", language, count=seconds)
    minutes = seconds // 60
    if minutes < 60:
        return text("duration_minutes", language, count=minutes)
    hours = minutes // 60
    if hours < 48:
        return text("duration_hours", language, count=hours)
    return text("duration_days", language, count=hours // 24)


def translate(source, language=EN):
    if QCoreApplication is not None:
        translated = QCoreApplication.translate(CONTEXT, source)
        if translated != source:
            return translated

    if language == EN:
        return source

    return _translation_map(language).get(source, source)


@lru_cache(maxsize=None)
def _translation_map(language):
    path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "i18n",
        "gbfs_now_{}.ts".format(language),
    )
    try:
        tree = ET.parse(path)
    except (OSError, ET.ParseError):
        return {}

    translations = {}
    for message in tree.findall(".//message"):
        source = message.findtext("source")
        translation = message.find("translation")
        if source is None or translation is None:
            continue
        if translation.get("type") == "unfinished":
            continue
        translations[source] = translation.text or ""
    return translations
