# -*- coding: utf-8 -*-

import html
import os

from qgis.PyQt.QtCore import Qt, QUrl
from qgis.PyQt.QtGui import QPixmap
from qgis.PyQt.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest

from . import compat
from .qt_compat import enum_value, network_reply_no_error




SYSTEM_LABELS = [
    "label_name",
    "label_system_type",
    "label_language",
    "label_operator",
    "label_start_date",
    "label_url",
    "label_license_url",
    "label_brand_terms_url",
    "label_terms_url",
    "label_privacy_url",
    "label_android",
    "label_ios",
]

LINK_TEXTS = {
    "label_url": "Website",
    "label_license_url": "License",
    "label_brand_terms_url": "Brand Terms",
    "label_terms_url": "Terms of Service",
    "label_privacy_url": "Privacy Policy",
    "label_android": "Android App",
    "label_ios": "iOS App",
}


def render(widget, system_information, language):
    item = compat.payload_data(system_information)
    name = compat.display_text(item.get("name"), language)
    system_id = compat.display_text(item.get("system_id"), language)
    widget.system_name = name or system_id or "GBFS"
    widget.system_layer_name = _layer_prefix(system_id or name or "GBFS")

    languages = item.get("languages", item.get("language", ""))
    rental_apps = item.get("rental_apps", {})
    brand_assets = item.get("brand_assets", {})

    _set_optional_text(widget, "label_name", widget.system_name)
    _set_optional_text(widget, "label_system_type", _system_type_text(widget, language))
    _set_optional_text(widget, "label_language", compat.display_text(languages, language))
    _set_optional_text(widget, "label_operator", compat.display_text(item.get("operator"), language))
    _set_optional_text(widget, "label_start_date", compat.display_text(item.get("start_date"), language))
    _set_optional_link(widget, "label_url", compat.display_text(item.get("url"), language))
    _set_optional_link(widget, "label_license_url", compat.display_text(item.get("license_url"), language))
    _set_link(
        _optional_label(widget, "label_brand_terms_url"),
        compat.display_text(brand_assets.get("brand_terms_url"), language),
        LINK_TEXTS["label_brand_terms_url"],
    )
    _set_optional_link(widget, "label_terms_url", compat.display_text(item.get("terms_url"), language))
    _set_optional_link(widget, "label_privacy_url", compat.display_text(item.get("privacy_url"), language))
    _set_link(
        _optional_label(widget, "label_android"),
        compat.display_text(
            compat.field_value({"rental_apps": rental_apps}, "rental_apps.android.store_uri"),
            language,
        ),
        LINK_TEXTS["label_android"],
    )
    _set_link(
        _optional_label(widget, "label_ios"),
        compat.display_text(
            compat.field_value({"rental_apps": rental_apps}, "rental_apps.ios.store_uri"),
            language,
        ),
        LINK_TEXTS["label_ios"],
    )
    _set_service_links(
        widget,
        [
            (LINK_TEXTS["label_url"], compat.display_text(item.get("url"), language)),
            (
                LINK_TEXTS["label_android"],
                compat.display_text(
                    compat.field_value(
                        {"rental_apps": rental_apps}, "rental_apps.android.store_uri"
                    ),
                    language,
                ),
            ),
            (
                LINK_TEXTS["label_ios"],
                compat.display_text(
                    compat.field_value(
                        {"rental_apps": rental_apps}, "rental_apps.ios.store_uri"
                    ),
                    language,
                ),
            ),
        ],
    )
    _set_service_summary(
        widget,
        widget.system_name,
        _system_type_text(widget, language),
        compat.display_text(item.get("operator"), language),
        compat.display_text(languages, language),
        compat.display_text(item.get("start_date"), language),
    )

    brand_image = _optional_label(widget, "brand_image")
    if brand_image is not None:
        _download_image(
            widget,
            brand_image,
            compat.display_text(brand_assets.get("brand_image_url"), language),
        )


def clear(widget):
    widget.system_name = "GBFS"
    widget.system_layer_name = "GBFS"
    for label_name in SYSTEM_LABELS:
        label = _optional_label(widget, label_name)
        if label is not None:
            label.clear()
    service_links_label = _optional_label(widget, "service_links_label")
    if service_links_label is not None:
        service_links_label.clear()
    service_summary_label = _optional_label(widget, "service_summary_label")
    if service_summary_label is not None:
        service_summary_label.clear()
    brand_image = _optional_label(widget, "brand_image")
    if brand_image is not None:
        brand_image.clear()


def _optional_label(widget, name):
    return getattr(widget, name, None)


def _set_optional_text(widget, name, value):
    label = _optional_label(widget, name)
    if label is not None:
        _set_text(label, value)


def _set_optional_link(widget, name, url):
    label = _optional_label(widget, name)
    if label is not None:
        _set_link(label, url, LINK_TEXTS.get(name, "Open Link"))


def _set_text(label, value):
    if label is None:
        return
    label.setText(value or "")


def _set_link(label, url, text="Open Link"):
    if label is None:
        return
    if not url:
        label.clear()
        return
    escaped = html.escape(url, quote=True)
    label.setOpenExternalLinks(True)
    label.setText('<a href="{0}">{1}</a>'.format(escaped, html.escape(text)))


def _set_service_links(widget, links):
    label = _optional_label(widget, "service_links_label")
    if label is None:
        return
    anchors = []
    for text, url in links:
        if url:
            anchors.append(
                '<a href="{0}">{1}</a>'.format(
                    html.escape(url, quote=True), html.escape(text)
                )
            )
    label.setText(" / ".join(anchors))


def _set_service_summary(widget, name, system_type, operator, language, start_date):
    label = _optional_label(widget, "service_summary_label")
    if label is None:
        return
    version = getattr(getattr(widget, "discovery", None), "version", "")
    lines = []
    if name:
        lines.append("<b>{}</b>".format(html.escape(name)))
    details = " · ".join(
        html.escape(value) for value in (system_type, operator) if value
    )
    if details:
        lines.append(details)
    metadata = [value for value in (language, start_date) if value]
    if version:
        metadata.append("GBFS v{}".format(version))
    if metadata:
        lines.append('<span style="color:#555555">{}</span>'.format(
            " · ".join(html.escape(value) for value in metadata)
        ))
    label.setText("<br>".join(lines))



def _system_type_text(widget, language):
    discovery = getattr(widget, "discovery", None)
    if discovery is None:
        return ""

    station_url = discovery.feed_url("station_information", language)
    vehicle_url = (
        discovery.feed_url("vehicle_status", language)
        or discovery.feed_url("free_bike_status", language)
    )

    if station_url:
        key = "system_type_station"
        fallback = "Station-based system"
    elif vehicle_url:
        key = "system_type_dockless"
        fallback = "Dockless system"
    else:
        key = "system_type_unknown"
        fallback = "Unknown"

    text_method = getattr(widget, "_text", None)
    if callable(text_method):
        return text_method(key)
    return fallback

def _download_image(widget, target_label, url):
    if not url:
        _set_fallback_image(target_label)
        return
    widget._brand_image_manager = QNetworkAccessManager()
    widget._brand_image_manager.finished.connect(
        lambda reply: _set_image(reply, target_label)
    )
    widget._brand_image_manager.get(QNetworkRequest(QUrl(url)))


def _set_image(reply, target_label):
    if reply.error() == network_reply_no_error(QNetworkReply):
        pixmap = QPixmap()
        pixmap.loadFromData(reply.readAll())
        if pixmap.isNull():
            _set_fallback_image(target_label)
        else:
            _set_pixmap(target_label, pixmap)
    else:
        _set_fallback_image(target_label)
    reply.deleteLater()


def _set_fallback_image(target_label):
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "no_image.png")
    pixmap = QPixmap(path)
    if pixmap.isNull():
        target_label.clear()
        return
    _set_pixmap(target_label, pixmap)


def _set_pixmap(target_label, pixmap):
    width = target_label.width() or target_label.maximumWidth() or 100
    height = target_label.height() or target_label.maximumHeight() or 80
    target_label.setPixmap(
        pixmap.scaled(
            width,
            height,
            enum_value(Qt, "AspectRatioMode", "KeepAspectRatio"),
            enum_value(Qt, "TransformationMode", "SmoothTransformation"),
        )
    )


def _layer_prefix(value):
    text = " ".join(str(value or "GBFS").split())
    if not text:
        return "GBFS"
    return text[:48]
