# -*- coding: utf-8 -*-

import json
import os
import traceback
from urllib.parse import urlparse

from qgis.PyQt import QtCore, QtGui, QtWidgets, uic
from qgis.PyQt.QtCore import QSettings, Qt, pyqtSignal
from qgis.core import Qgis, QgsMessageLog

from . import gbfs_now_search_dialog as search_dialog
from .gbfs_now_core import feed_preview, system_view, ui_text, vehicle_types_view
from .gbfs_now_core.catalog import prefetch_systems_catalog
from .gbfs_now_core.client import GbfsClient, GbfsClientError
from .gbfs_now_core.compat import DEFAULT_LANGUAGE, records
from .gbfs_now_core.labels import label_language
from .gbfs_now_core.layers import LayerBuilder
from .gbfs_now_core.qt_compat import (
    class_enum,
    compatible_qt,
    qgis_message_level,
    size_policy,
)


qt = compatible_qt(Qt)


FORM_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "gbfs_now_dockwidget_base.ui")
)

FAVORITES_KEY = "GBFS-NOW/favorite_urls"
LAST_URL_KEY = "GBFS-NOW/last_url"
MAX_FAVORITES = 10


def _debug(message, warning=False):
    """Write detailed diagnostics to QGIS Log Messages > GBFS-NOW DEBUG."""
    QgsMessageLog.logMessage(
        str(message),
        "GBFS-NOW DEBUG",
        qgis_message_level(Qgis, "Warning") if warning else qgis_message_level(Qgis, "Info"),
    )


DEFAULT_SELECTED_FEEDS = {
    "station_information": True,
    "station_status": False,
    "vehicle_status": True,
}

FEED_CARD_STYLE = """
QFrame#feedCard {
    border: 1px solid #c8c8c8;
    border-radius: 4px;
    background: #ffffff;
}
QFrame#feedCard[selected="true"] {
    border: 1px solid #2b7ddd;
    background: #eef6ff;
}
QFrame#feedCard[available="false"] {
    border-color: #d8d8d8;
    background: #f7f7f7;
}
QLabel#feedTitle {
    font-weight: 600;
}
QLabel#feedMeta {
    color: #555555;
}
QFrame#feedCard[available="false"] QLabel {
    color: #777777;
}
"""

LANGUAGE_BUTTON_STYLE = """
QPushButton {
    min-height: 28px;
    border: 1px solid #c8c8c8;
    border-radius: 4px;
    background: #ffffff;
}
QPushButton:checked {
    border: 1px solid #2b7ddd;
    background: #eef6ff;
}
"""

class FeedCard(QtWidgets.QFrame):
    clicked = pyqtSignal(str)

    def __init__(self, feed_name, icon_path, parent=None):
        super().__init__(parent)
        self.feed_name = feed_name
        self.available = False
        self.setObjectName("feedCard")
        self.setStyleSheet(FEED_CARD_STYLE)
        self.setMinimumHeight(48)
        self.setCursor(qt.PointingHandCursor)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(7, 4, 7, 4)
        layout.setSpacing(7)

        self.icon_label = QtWidgets.QLabel(self)
        self.icon_label.setFixedSize(30, 30)
        self.icon_label.setAlignment(qt.AlignCenter)
        pixmap = QtGui.QPixmap(icon_path)
        if not pixmap.isNull():
            self.icon_label.setPixmap(
                pixmap.scaled(25, 25, qt.KeepAspectRatio, qt.SmoothTransformation)
            )
        layout.addWidget(self.icon_label)

        text_layout = QtWidgets.QVBoxLayout()
        text_layout.setSpacing(1)
        self.title_label = QtWidgets.QLabel(self)
        self.title_label.setObjectName("feedTitle")
        self.meta_label = QtWidgets.QLabel(self)
        self.meta_label.setObjectName("feedMeta")
        self.meta_label.setWordWrap(False)
        text_layout.addWidget(self.title_label)
        text_layout.addWidget(self.meta_label)
        layout.addLayout(text_layout, 1)

        self.selected_label = QtWidgets.QLabel(self)
        self.selected_label.setFixedSize(18, 18)
        self.selected_label.setAlignment(qt.AlignCenter)
        layout.addWidget(self.selected_label)

    def set_preview(self, title, meta, selected, available):
        self.available = available
        self.title_label.setText(title)
        self.meta_label.setText(meta)
        self.setProperty("selected", selected)
        self.setProperty("available", available)
        self.setCursor(qt.PointingHandCursor if available else qt.ArrowCursor)

        if selected:
            icon = self.style().standardIcon(
                class_enum(QtWidgets.QStyle, "SP_DialogApplyButton")
            )
            self.selected_label.setPixmap(icon.pixmap(16, 16))
        else:
            self.selected_label.clear()

        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def mousePressEvent(self, event):
        if self.available and event.button() == qt.LeftButton:
            self.clicked.emit(self.feed_name)
        super().mousePressEvent(event)


class gbfs_nowDockWidget(QtWidgets.QDockWidget, FORM_CLASS):
    closingPlugin = pyqtSignal()

    def __init__(self, parent=None):
        super(gbfs_nowDockWidget, self).__init__(parent)
        self.setupUi(self)

        self.client = GbfsClient()
        self.layer_builder = LayerBuilder(os.path.dirname(__file__))
        self.discovery = None
        self.gbfs_language = None
        self.loaded_url = ""
        self.stations_info = []
        self.system_name = "GBFS"
        self.system_layer_name = "GBFS"
        self.feed_cache = {}
        self.layer_previews = []
        self.feed_cards = {}
        self.language_buttons = {}
        self.selected_feeds = set()
        self.ui_language = ui_text.EN
        self._busy = False
        self._content_stale = False
        self._empty_labels = {}

        self._configure_ui()
        self.toolButton.clicked.connect(self.show_search_dialog)
        self.favoriteButton.clicked.connect(self._show_favorites_menu)
        self.searchButton.clicked.connect(self.search_gbfs_dataset)
        self.viewButton.clicked.connect(self.view_gbfs_dataset)
        self.serviceToggleButton.toggled.connect(self._toggle_service_information)
        self.vehicleInfoToggleButton.toggled.connect(self._toggle_vehicle_information)
        self.gbfs_url.textChanged.connect(self._on_url_changed)
        prefetch_systems_catalog()

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()

    def show_search_dialog(self):
        gbfs_url, accepted = search_dialog.gbfs_now_search_Dialog(self).get_url()
        if accepted and gbfs_url:
            self.gbfs_url.setText(gbfs_url)

    def search_gbfs_dataset(self):
        gbfs_url = self.gbfs_url.text().strip()
        if not gbfs_url:
            self._show_error(self._text("url_required"))
            return

        self._set_busy(True)
        try:
            self.feed_cache = {}
            self.layer_previews = []
            self.selected_feeds = set()
            self.discovery = self.client.load_discovery(gbfs_url)
            self.loaded_url = gbfs_url
            self._set_loaded_content_stale(False)
            self._set_status("")

            languages = self.discovery.languages
            self.gbfs_language = languages[0] if len(languages) == 1 else None
            self._render_language_buttons(languages)
            self._render_service_information()
            self._set_vehicle_information_empty("data_not_loaded")

            if self.gbfs_language:
                self._render_feed_availability(reset_selection=True)
                self._flush_ui()
                self._refresh_feed_details(reset_selection=False)
                self._render_vehicle_information()
            else:
                self._clear_feed_cards("select_language_first")
                self._set_vehicle_information_empty("select_language_first")

            self._show_loaded_sections()
        except (GbfsClientError, ValueError) as error:
            self.discovery = None
            self.loaded_url = ""
            self.feed_cache = {}
            self.layer_previews = []
            self.selected_feeds = set()
            self._clear_loaded_sections()
            self._show_error(self._text("load_error", error=error))
        finally:
            QSettings().setValue(LAST_URL_KEY, gbfs_url)
            self._set_busy(False)

    def view_gbfs_dataset(self):
        if not self.discovery or self._content_stale:
            _debug(
                "[MAP ABORT] discovery={} content_stale={}".format(
                    bool(self.discovery), self._content_stale
                ),
                warning=True,
            )
            return

        label_lang = label_language(self.jpStyle.isChecked())
        selected_feeds = self._selected_layer_feeds()
        if not selected_feeds:
            _debug("[MAP ABORT] no layers selected", warning=True)
            self._show_error(self._text("no_layers_selected"))
            return

        _debug(
            "[MAP START] selected_feeds={} language={} label_language={} system={}".format(
                sorted(selected_feeds),
                self.gbfs_language,
                label_lang,
                self._layer_system_name(),
            )
        )

        self._set_busy(True)
        try:
            self.layer_builder.replace_existing = True

            _debug("[MAP SERVICE INFO START]")
            self._render_service_information()
            _debug("[MAP SERVICE INFO OK]")

            station_available = self._feed_available("station_information")
            _debug(
                "[STATION INFORMATION AVAILABLE] {}".format(station_available)
            )

            station_feed = (
                self._get_feed("station_information", self.gbfs_language)
                if station_available
                else None
            )

            _debug(
                "[STATION FEED RESULT] exists={} type={}".format(
                    station_feed is not None, type(station_feed).__name__
                )
            )

            if isinstance(station_feed, dict):
                station_data = station_feed.get("data")
                _debug(
                    "[STATION FEED STRUCTURE] top_keys={} data_type={} data_keys={}".format(
                        list(station_feed.keys()),
                        type(station_data).__name__,
                        list(station_data.keys())
                        if isinstance(station_data, dict)
                        else None,
                    )
                )

            self.stations_info = []

            if station_feed and "station_information" in selected_feeds:
                _debug(
                    "[BEFORE ADD STATIONS] station_feed_type={} system={}".format(
                        type(station_feed).__name__, self._layer_system_name()
                    )
                )

                self.stations_info = self.layer_builder.add_stations(
                    self._layer_system_name(),
                    station_feed,
                    self.gbfs_language,
                    label_lang,
                )

                _debug(
                    "[AFTER ADD STATIONS] count={}".format(
                        len(self.stations_info)
                    )
                )

            elif station_feed:
                _debug(
                    "[STATION INFORMATION NOT SELECTED] extracting records only"
                )
                self.stations_info = records(station_feed, "stations")
                _debug(
                    "[STATION RECORDS EXTRACTED] count={}".format(
                        len(self.stations_info)
                    )
                )
            else:
                _debug("[NO STATION FEED]", warning=True)

            if "station_status" in selected_feeds:
                _debug("[BEFORE GET STATION STATUS]")
                status_feed = self._get_feed(
                    "station_status", self.gbfs_language
                )
                _debug(
                    "[STATION STATUS FEED RESULT] exists={} type={}".format(
                        status_feed is not None, type(status_feed).__name__
                    )
                )
                if status_feed:
                    _debug(
                        "[BEFORE ADD STATION STATUS] stations={}".format(
                            len(self.stations_info)
                        )
                    )
                    self.layer_builder.add_station_status(
                        self._layer_system_name(),
                        status_feed,
                        self.stations_info,
                        self.gbfs_language,
                        label_lang,
                    )
                    _debug("[AFTER ADD STATION STATUS]")

            vehicle_available = self._feed_available("vehicle_status")
            _debug(
                "[VEHICLE STATUS AVAILABLE] {}".format(vehicle_available)
            )

            vehicle_feed = (
                self._get_feed("vehicle_status", self.gbfs_language)
                if vehicle_available
                else None
            )

            _debug(
                "[VEHICLE FEED RESULT] exists={} type={}".format(
                    vehicle_feed is not None, type(vehicle_feed).__name__
                )
            )

            if vehicle_feed and "vehicle_status" in selected_feeds:
                _debug(
                    "[BEFORE ADD VEHICLES] stations={}".format(
                        len(self.stations_info)
                    )
                )
                self.layer_builder.add_vehicles(
                    self._layer_system_name(),
                    vehicle_feed,
                    self.stations_info,
                    self.gbfs_language,
                    label_lang,
                )
                _debug("[AFTER ADD VEHICLES]")

            _debug(
                "[MAP OK] selected_feeds={}".format(
                    sorted(selected_feeds)
                )
            )
            self._set_status(
                self._text("layers_added", count=len(selected_feeds))
            )

        except Exception as error:
            _debug(
                "[MAP FATAL ERROR] type={} error={}\n{}".format(
                    type(error).__name__,
                    error,
                    traceback.format_exc(),
                ),
                warning=True,
            )
            self._show_error(self._text("render_error", error=error))

        finally:
            self._set_busy(False)

    def get_gbfs_each_url(self, filename):
        if not self.discovery:
            return None
        return self.discovery.feed_url(filename, self.gbfs_language)

    def _configure_ui(self):
        self.ui_language = ui_text.language_for_locale(
            QSettings().value("locale/userLocale", "")
        )
        self.gbfs_url.setPlaceholderText("https://example.com/gbfs.json")
        self.gbfs_url.setClearButtonEnabled(True)
        self.jpStyle.setChecked(self.ui_language == ui_text.JA)
        self.jpStyle.setStyleSheet("color: #555555;")

        self.serviceToggleButton.setCheckable(True)
        self.serviceToggleButton.setChecked(True)
        self.serviceToggleButton.setVisible(False)
        self.vehicleInfoToggleButton.setCheckable(True)
        self.vehicleInfoToggleButton.setChecked(False)
        self.vehicleInfoEmptyLabel.setStyleSheet("color: #777777;")
        self._configure_source_controls()
        self._configure_service_information()
        self._install_empty_labels()
        self._install_vehicle_types_table()
        self._apply_ui_texts()
        self._clear_loaded_sections()

        last_url = str(QSettings().value(LAST_URL_KEY, "") or "").strip()
        if last_url:
            self.gbfs_url.setText(last_url)

    def _apply_ui_texts(self):
        self.setWindowTitle(self._text("plugin_title"))
        self.sourceTitleLabel.setText(self._text("source_section"))
        self.sourceUrlLabel.setText(self._text("gbfs_url"))
        self.languageTitleLabel.setText(self._text("language_section"))
        self.feedsTitleLabel.setText(self._text("feeds_section"))
        self.serviceTitleLabel.setText(self._text("service_section"))
        self.vehicleInfoTitleLabel.setText(self._text("vehicle_info_section"))
        self.vehicleInfoEmptyLabel.setText(self._text("vehicle_info_empty"))
        self.searchButton.setText(self._text("load_gbfs"))
        self.viewButton.setText(self._text("add_to_map"))
        self.favoriteButton.setToolTip(self._text("favorite_tooltip"))
        self.favoriteButton.setText("\u2606")
        self.toolButton.setToolTip(self._text("catalog_tooltip"))
        self.toolButton.setText("...")
        self.jpStyle.setText(self._text("japanese_field_names"))
        self.systemFieldLabel.setText(self._text("system_label"))
        self.systemTypeFieldLabel.setText(self._text("system_type_label"))
        self.operatorFieldLabel.setText(self._text("operator_label"))
        self.languageFieldLabel.setText(self._text("language_label"))
        self.startDateFieldLabel.setText(self._text("service_start_label"))
        self.urlFieldLabel.setText(self._text("service_url_label"))
        self.androidFieldLabel.setText(self._text("android_store_label"))
        self.iosFieldLabel.setText(self._text("ios_store_label"))
        self.dataFormatFieldLabel.setText(self._text("data_format_label"))
        for label in self._empty_labels.values():
            label.setText(self._text("data_not_loaded"))
        self._toggle_service_information(self.serviceToggleButton.isChecked())
        self._toggle_vehicle_information(self.vehicleInfoToggleButton.isChecked())

    def _install_empty_labels(self):
        self._empty_labels = {
            "language": self._empty_label(self.languageSection),
            "feeds": self._empty_label(self.feedsSection),
            "service": self._empty_label(self.serviceSection),
        }
        self.languageLayout.addWidget(self._empty_labels["language"])
        self.feedsOuterLayout.addWidget(self._empty_labels["feeds"])
        self.serviceLayout.addWidget(self._empty_labels["service"])

    def _empty_label(self, parent):
        label = QtWidgets.QLabel(parent)
        label.setStyleSheet("color: #777777;")
        label.setWordWrap(True)
        return label

    def _install_vehicle_types_table(self):
        self.vehicle_types_table = QtWidgets.QTableView(self.vehicleInfoContent)
        self.vehicle_types_table.setIconSize(QtCore.QSize(190, 190))
        self.vehicle_types_table.setSelectionMode(
            class_enum(QtWidgets.QAbstractItemView, "NoSelection")
        )
        self.vehicle_types_table.setEditTriggers(
            class_enum(QtWidgets.QAbstractItemView, "NoEditTriggers")
        )
        self.vehicle_types_table.setAlternatingRowColors(False)
        self.vehicle_types_table.setVerticalScrollBarPolicy(qt.ScrollBarAlwaysOff)
        self.vehicle_types_table.setHorizontalScrollBarPolicy(qt.ScrollBarAlwaysOff)
        self.vehicle_types_table.horizontalHeader().setStretchLastSection(True)
        self.vehicleInfoLayout.addWidget(self.vehicle_types_table)

    def _configure_source_controls(self):
        self.sourceActionLayout.removeWidget(self.searchButton)
        self.sourceControlsLayout.addWidget(self.searchButton)
        self.searchButton.setMinimumSize(QtCore.QSize(72, 28))
        self.searchButton.setMaximumHeight(28)

    def _configure_service_information(self):
        for name in (
            "systemFieldLabel",
            "label_name",
            "systemTypeFieldLabel",
            "label_system_type",
            "operatorFieldLabel",
            "label_operator",
            "languageFieldLabel",
            "label_language",
            "startDateFieldLabel",
            "label_start_date",
            "label_url",
            "label_license_url",
            "label_brand_terms_url",
            "label_terms_url",
            "label_privacy_url",
            "label_android",
            "label_ios",
            "dataFormatFieldLabel",
            "label_type",
        ):
            label = getattr(self, name, None)
            if label is not None:
                self.serviceGrid.removeWidget(label)
                label.hide()

        for name in (
            "urlFieldLabel",
            "label_url",
            "androidFieldLabel",
            "label_android",
            "iosFieldLabel",
            "label_ios",
        ):
            widget = getattr(self, name)
            self.serviceGrid.removeWidget(widget)
            widget.hide()

        self.service_summary_label = QtWidgets.QLabel(self.serviceContent)
        rich_text = getattr(Qt, "RichText", None)
        if rich_text is None:
            rich_text = Qt.TextFormat.RichText
        self.service_summary_label.setTextFormat(rich_text)
        self.service_summary_label.setWordWrap(True)
        self.service_summary_label.setAlignment(qt.AlignTop | qt.AlignLeft)
        self.service_summary_label.setSizePolicy(
            size_policy(QtWidgets.QSizePolicy, "Expanding"),
            size_policy(QtWidgets.QSizePolicy, "Preferred"),
        )
        self.serviceGrid.addWidget(self.service_summary_label, 0, 1, 9, 2)

        self.service_links_label = QtWidgets.QLabel(self.serviceContent)
        self.service_links_label.setOpenExternalLinks(True)
        self.service_links_label.setWordWrap(False)
        self.service_links_label.setSizePolicy(
            size_policy(QtWidgets.QSizePolicy, "Preferred"),
            size_policy(QtWidgets.QSizePolicy, "Fixed"),
        )
        self.serviceGrid.addWidget(self.service_links_label, 9, 0, 1, 3)

    def _render_language_buttons(self, languages):
        self._clear_layout(self.languageGrid)
        self.language_buttons = {}

        for index, language in enumerate(languages):
            button = QtWidgets.QPushButton(self._language_label(language), self)
            button.setCheckable(True)
            button.setStyleSheet(LANGUAGE_BUTTON_STYLE)
            button.setToolTip(str(language))
            button.clicked.connect(
                lambda checked=False, value=language: self._select_language(value)
            )
            self.language_buttons[language] = button
            self.languageGrid.addWidget(button, index // 5, index % 5)

        self._update_language_button_states()
        self.languageButtonsContainer.setVisible(bool(languages))
        self._empty_labels["language"].setVisible(not bool(languages))

    def _language_label(self, language):
        if language == DEFAULT_LANGUAGE:
            return self._text("default_language")
        return str(language).split("-", 1)[0]

    def _select_language(self, language):
        if not self.discovery:
            return
        if language == self.gbfs_language and self.layer_previews:
            self._update_language_button_states()
            return

        self.gbfs_language = language
        self._update_language_button_states()
        self._set_busy(True)
        try:
            self._render_feed_availability(reset_selection=True)
            self._show_loaded_sections()
            self._flush_ui()
            self._refresh_feed_details(reset_selection=False)
            self._render_service_information()
            self._render_vehicle_information()
        except (GbfsClientError, ValueError) as error:
            self._show_error(self._text("refresh_error", error=error))
        finally:
            self._set_busy(False)

    def _update_language_button_states(self):
        for language, button in self.language_buttons.items():
            button.setChecked(language == self.gbfs_language)

    def _render_feed_availability(self, reset_selection=False):
        if not self.discovery or not self.gbfs_language:
            self._clear_feed_cards("data_not_loaded")
            return

        previews = []
        for layer_name, feed_name, record_keys in feed_preview.LAYER_FEEDS:
            url = self.discovery.feed_url(feed_name, self.gbfs_language)
            previews.append(
                feed_preview.FeedPreview(
                    layer_name,
                    feed_name,
                    url=url,
                    error="" if url else "Feed not published",
                )
            )

        self.layer_previews = previews
        self._apply_preview_selection(reset_selection)
        self._render_feed_cards()
        self._update_create_button()

    def _refresh_feed_details(self, reset_selection=False):
        if not self.discovery or not self.gbfs_language:
            self._clear_feed_cards("data_not_loaded")
            return

        previews = []
        for layer_name, feed_name, record_keys in feed_preview.LAYER_FEEDS:
            url = self.discovery.feed_url(feed_name, self.gbfs_language)
            if not url:
                previews.append(
                    feed_preview.summarize_feed(layer_name, feed_name, record_keys)
                )
                continue

            try:
                feed_json = self._get_feed(feed_name, self.gbfs_language)
                previews.append(
                    feed_preview.summarize_feed(
                        layer_name, feed_name, record_keys, url, feed_json
                    )
                )
            except (GbfsClientError, ValueError) as error:
                previews.append(
                    feed_preview.summarize_feed(
                        layer_name, feed_name, record_keys, url, error=error
                    )
                )

        self.layer_previews = previews
        self._apply_preview_selection(reset_selection)
        self._render_feed_cards()
        self._update_create_button()

    def _apply_preview_selection(self, reset_selection):
        available_feeds = {
            preview.feed_name for preview in self.layer_previews if preview.available
        }
        if reset_selection:
            self.selected_feeds = {
                feed_name
                for feed_name in available_feeds
                if DEFAULT_SELECTED_FEEDS.get(feed_name, False)
            }
        else:
            self.selected_feeds.intersection_update(available_feeds)
            if not self.selected_feeds:
                self.selected_feeds = {
                    feed_name
                    for feed_name in available_feeds
                    if DEFAULT_SELECTED_FEEDS.get(feed_name, False)
                }

    def _get_feed(self, feed_name, language=None):
        if not self.discovery:
            _debug(
                "[GET FEED ABORT] name={} discovery=None".format(feed_name),
                warning=True,
            )
            return None

        cache_key = (language or "", feed_name)

        if cache_key in self.feed_cache:
            result = self.feed_cache[cache_key]
            _debug(
                "[GET FEED CACHE] name={} language={} exists={} type={}".format(
                    feed_name,
                    language,
                    result is not None,
                    type(result).__name__,
                )
            )
            return result

        try:
            url = self.discovery.feed_url(feed_name, language)
        except Exception as error:
            _debug(
                "[GET FEED URL ERROR] name={} language={} type={} error={}".format(
                    feed_name,
                    language,
                    type(error).__name__,
                    error,
                ),
                warning=True,
            )
            raise

        _debug(
            "[GET FEED] name={} language={} url={}".format(
                feed_name, language, url
            )
        )

        if self._can_use_discovery_system_information(feed_name, language):
            _debug(
                "[GET FEED USE DISCOVERY CACHE] name={}".format(feed_name)
            )
            self.feed_cache[cache_key] = self.discovery.system_information
        else:
            self.feed_cache[cache_key] = self.client.get_feed(
                self.discovery, feed_name, language
            )

        result = self.feed_cache[cache_key]

        if isinstance(result, dict):
            data = result.get("data")
            data_keys = list(data.keys()) if isinstance(data, dict) else None
            _debug(
                "[GET FEED OK] name={} type={} top_keys={} data_type={} data_keys={}".format(
                    feed_name,
                    type(result).__name__,
                    list(result.keys()),
                    type(data).__name__,
                    data_keys,
                )
            )
        else:
            _debug(
                "[GET FEED OK] name={} type={} exists={}".format(
                    feed_name, type(result).__name__, result is not None
                )
            )

        return result

    def _can_use_discovery_system_information(self, feed_name, language):
        if feed_name != "system_information" or not self.discovery.system_information:
            return False
        if self.discovery.is_flat:
            return True
        return not language or language == self.discovery.default_language()

    def _clear_feed_cards(self, message_key="data_not_loaded"):
        self.layer_previews = []
        self.selected_feeds = set()
        self._clear_layout(self.feedsLayout)
        self.feed_cards = {}
        self.feedCardsContainer.setVisible(False)
        self._show_empty("feeds", message_key)
        self._update_create_button()

    def _render_feed_cards(self):
        self._clear_layout(self.feedsLayout)
        self.feed_cards = {}

        for preview in self.layer_previews:
            card = FeedCard(
                preview.feed_name,
                self._feed_icon_path(preview.feed_name),
                self.feedCardsContainer,
            )
            card.clicked.connect(self._toggle_feed_selection)
            card.set_preview(
                self._feed_title(preview.feed_name),
                self._feed_meta(preview),
                preview.feed_name in self.selected_feeds,
                preview.available,
            )
            self.feed_cards[preview.feed_name] = card
            self.feedsLayout.addWidget(card)

        self.feedCardsContainer.setVisible(bool(self.layer_previews))
        self._empty_labels["feeds"].setVisible(not bool(self.layer_previews))

    def _toggle_feed_selection(self, feed_name):
        if not self._feed_available(feed_name):
            return
        if feed_name in self.selected_feeds:
            self.selected_feeds.remove(feed_name)
        else:
            self.selected_feeds.add(feed_name)
        self._render_feed_cards()
        self._update_create_button()

    def _feed_title(self, feed_name):
        labels = {
            "station_information": "feed_station_information",
            "station_status": "feed_station_status",
            "vehicle_status": "feed_vehicle_status",
        }
        return self._text(labels.get(feed_name, feed_name))

    def _feed_icon_path(self, feed_name):
        filenames = {
            "station_information": "station.png",
            "station_status": "station_now.png",
            "vehicle_status": "bike.png",
        }
        return os.path.join(
            os.path.dirname(__file__), filenames.get(feed_name, "station.png")
        )

    def _feed_meta(self, preview):
        if not preview.available:
            return self._text("feed_missing")
        if preview.record_count is None:
            return self._text("available")

        updated = ui_text.format_updated_age(preview.age_seconds, self.ui_language)
        if not updated:
            updated = preview.last_updated or self._text("unknown_value")
        return "{} / {}".format(self._feed_count(preview), updated)

    def _feed_count(self, preview):
        key = "vehicle_count" if preview.feed_name == "vehicle_status" else "station_count"
        return self._text(key, count="{:,}".format(preview.record_count))

    def _selected_layer_feeds(self):
        if self._content_stale:
            return []
        return [
            preview.feed_name
            for preview in self.layer_previews
            if preview.feed_name in self.selected_feeds and preview.available
        ]

    def _feed_available(self, feed_name):
        return any(
            preview.feed_name == feed_name and preview.available
            for preview in self.layer_previews
        )

    def _render_service_information(self):
        if not self.discovery:
            system_view.clear(self)
            self.serviceToggleButton.setVisible(False)
            self.serviceContent.setVisible(False)
            self._show_empty("service", "data_not_loaded")
            return

        language = self.gbfs_language or self.discovery.default_language()
        system_feed = self._get_feed("system_information", language)
        if system_feed:
            system_view.render(self, system_feed, language)
            self.serviceToggleButton.setVisible(False)
            self.serviceContent.setVisible(True)
            self._empty_labels["service"].setVisible(False)
        else:
            system_view.clear(self)
            self.serviceToggleButton.setVisible(False)
            self.serviceContent.setVisible(False)
            self._show_empty("service", "data_not_loaded")
        self._set_data_format()

    def _set_data_format(self):
        if self.discovery:
            self.label_type.setText(
                self._text("data_format_value", version=self.discovery.version)
            )
        else:
            self.label_type.clear()

    def _render_vehicle_information(self):
        if not self.discovery or not self.gbfs_language:
            self._set_vehicle_information_empty("data_not_loaded")
            return

        if not self.discovery.feed_url("vehicle_types", self.gbfs_language):
            self._set_vehicle_information_empty("vehicle_info_empty")
            return

        vehicle_types_feed = self._get_feed("vehicle_types", self.gbfs_language)
        vehicle_types = records(vehicle_types_feed, "vehicle_types")
        if not vehicle_types:
            self._set_vehicle_information_empty("vehicle_info_empty")
            return

        self.vehicleInfoTitleLabel.setEnabled(True)
        self.vehicleInfoToggleButton.setVisible(True)
        self.vehicleInfoToggleButton.setEnabled(True)
        self.vehicleInfoEmptyLabel.setVisible(False)
        vehicle_types_view.render(
            self, vehicle_types_feed, self.gbfs_language, os.path.dirname(__file__)
        )
        self.vehicleInfoContent.setVisible(self.vehicleInfoToggleButton.isChecked())
        self._toggle_vehicle_information(self.vehicleInfoToggleButton.isChecked())

    def _set_vehicle_information_empty(self, message_key):
        if hasattr(self, "vehicle_types_table"):
            vehicle_types_view.clear(self)
        self.vehicleInfoContent.setVisible(False)
        self.vehicleInfoToggleButton.setVisible(False)
        self.vehicleInfoToggleButton.setEnabled(False)
        self.vehicleInfoTitleLabel.setEnabled(message_key != "vehicle_info_empty")
        self.vehicleInfoEmptyLabel.setText(self._text(message_key))
        self.vehicleInfoEmptyLabel.setVisible(True)
        self.vehicleInfoEmptyLabel.setEnabled(False)

    def _clear_loaded_sections(self):
        self._clear_layout(self.languageGrid)
        self.language_buttons = {}
        self.languageButtonsContainer.setVisible(False)
        self._show_empty("language", "data_not_loaded")
        self._clear_feed_cards("data_not_loaded")
        self.addMapContainer.setVisible(False)
        self.serviceToggleButton.setVisible(False)
        self.serviceContent.setVisible(False)
        self._show_empty("service", "data_not_loaded")
        self._set_vehicle_information_empty("data_not_loaded")
        self.result_get_gbfs.clear()
        self.result_get_gbfs.setVisible(False)
        system_view.clear(self)
        self._set_loaded_content_stale(False)
        self._update_create_button()

    def _show_loaded_sections(self):
        self.languageSection.setVisible(True)
        self.feedsSection.setVisible(True)
        self.serviceSection.setVisible(True)
        self.vehicleSection.setVisible(True)
        self.languageButtonsContainer.setVisible(bool(self.language_buttons))
        self._empty_labels["language"].setVisible(not bool(self.language_buttons))
        self.feedCardsContainer.setVisible(bool(self.layer_previews))
        self.addMapContainer.setVisible(bool(self.layer_previews and self.gbfs_language))
        self._update_create_button()

    def _show_empty(self, name, message_key):
        label = self._empty_labels.get(name)
        if label is not None:
            label.setText(self._text(message_key))
            label.setVisible(True)

    def _toggle_service_information(self, checked):
        self.serviceContent.setVisible(checked and self.serviceToggleButton.isVisible())
        self.serviceToggleButton.setArrowType(qt.UpArrow if checked else qt.DownArrow)
        self.serviceToggleButton.setToolTip(
            self._text("collapse_service") if checked else self._text("expand_service")
        )

    def _toggle_vehicle_information(self, checked):
        self.vehicleInfoContent.setVisible(
            checked and self.vehicleInfoToggleButton.isVisible()
        )
        self.vehicleInfoToggleButton.setArrowType(qt.UpArrow if checked else qt.DownArrow)
        self.vehicleInfoToggleButton.setToolTip(
            self._text("collapse_vehicle") if checked else self._text("expand_vehicle")
        )

    def _on_url_changed(self, value):
        if not self.discovery:
            return
        self._set_loaded_content_stale(str(value or "").strip() != self.loaded_url)

    def _set_loaded_content_stale(self, stale):
        self._content_stale = stale
        for section in (
            self.languageSection,
            self.feedsSection,
            self.addMapContainer,
            self.serviceSection,
            self.vehicleSection,
        ):
            section.setEnabled(not stale)
            self._set_opacity(section, 0.55 if stale else 1.0)
        self._update_create_button()

    @staticmethod
    def _set_opacity(widget, opacity):
        if opacity >= 1:
            widget.setGraphicsEffect(None)
            return
        effect = QtWidgets.QGraphicsOpacityEffect(widget)
        effect.setOpacity(opacity)
        widget.setGraphicsEffect(effect)

    def _layer_system_name(self):
        return getattr(self, "system_layer_name", None) or self.system_name or "GBFS"

    def _favorite_entries(self):
        value = QSettings().value(FAVORITES_KEY, "[]")
        if isinstance(value, list):
            raw_items = value
        else:
            try:
                raw_items = json.loads(str(value or "[]"))
            except ValueError:
                raw_items = []

        entries = []
        for item in raw_items:
            if isinstance(item, dict):
                url = str(item.get("url", "")).strip()
                name = str(item.get("name", "")).strip()
            else:
                url = str(item or "").strip()
                name = ""
            if url:
                entries.append({"name": name or self._name_from_url(url), "url": url})
        return entries[:MAX_FAVORITES]

    def _save_favorite_entries(self, entries):
        QSettings().setValue(
            FAVORITES_KEY,
            json.dumps(entries[:MAX_FAVORITES], ensure_ascii=False),
        )

    def _show_favorites_menu(self):
        menu = QtWidgets.QMenu(self)
        save_action = menu.addAction(self._text("save_current_url"))
        save_action.triggered.connect(self._save_current_favorite)

        entries = self._favorite_entries()
        menu.addSeparator()
        if entries:
            for entry in entries:
                action = menu.addAction(self._favorite_label(entry))
                action.triggered.connect(
                    lambda checked=False, url=entry["url"]: self._apply_favorite_url(url)
                )

            remove_menu = menu.addMenu(self._text("remove_favorite"))
            for entry in entries:
                action = remove_menu.addAction(self._favorite_label(entry))
                action.triggered.connect(
                    lambda checked=False, url=entry["url"]: self._remove_favorite(url)
                )
        else:
            empty_action = menu.addAction(self._text("no_favorites"))
            empty_action.setEnabled(False)

        position = self.favoriteButton.mapToGlobal(
            QtCore.QPoint(0, self.favoriteButton.height())
        )
        exec_menu = getattr(menu, "exec_", None)
        if exec_menu is None:
            exec_menu = getattr(menu, "exec")
        exec_menu(position)

    def _save_current_favorite(self):
        url = self.gbfs_url.text().strip()
        if not url:
            self._set_status(self._text("url_required"))
            return

        entries = [entry for entry in self._favorite_entries() if entry["url"] != url]
        entries.insert(0, {"name": self._current_service_name(url), "url": url})
        self._save_favorite_entries(entries)
        QSettings().setValue(LAST_URL_KEY, url)
        self._set_status(self._text("added_favorite"))

    def _remove_favorite(self, url):
        entries = [entry for entry in self._favorite_entries() if entry["url"] != url]
        self._save_favorite_entries(entries)
        self._set_status(self._text("removed_favorite"))

    def _apply_favorite_url(self, url):
        self.gbfs_url.setText(url)
        QSettings().setValue(LAST_URL_KEY, url)

    def _favorite_label(self, entry):
        return "{}[{}]".format(entry["name"], entry["url"])

    def _current_service_name(self, url):
        if self.system_name and self.system_name != "GBFS":
            return self.system_name
        return self._name_from_url(url)

    @staticmethod
    def _name_from_url(url):
        parsed = urlparse(url)
        return parsed.netloc or "GBFS"

    def _show_error(self, message):
        self._set_status(message)
        QtWidgets.QMessageBox.warning(self, "GBFS-NOW", message)

    def _set_status(self, message):
        self.result_get_gbfs.setText(message or "")
        self.result_get_gbfs.setVisible(bool(message))

    def _set_busy(self, busy):
        self._busy = busy
        if busy:
            QtWidgets.QApplication.setOverrideCursor(qt.WaitCursor)
        else:
            QtWidgets.QApplication.restoreOverrideCursor()

        enabled = not busy
        for widget in (self.searchButton, self.toolButton, self.favoriteButton):
            widget.setEnabled(enabled)
        for button in self.language_buttons.values():
            button.setEnabled(enabled and not self._content_stale)
        self._update_create_button()

    def _update_create_button(self):
        can_create = (
            bool(self.discovery)
            and bool(self.gbfs_language)
            and bool(self._selected_layer_feeds())
            and not self._content_stale
            and not self._busy
        )
        self.viewButton.setEnabled(can_create)
        self.addMapContainer.setVisible(
            bool(self.discovery) and bool(self.gbfs_language) and bool(self.layer_previews)
        )

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            child_layout = item.layout()
            if widget is not None:
                widget.deleteLater()
            elif child_layout is not None:
                self._clear_layout(child_layout)

    @staticmethod
    def _flush_ui():
        QtWidgets.QApplication.processEvents(
            class_enum(QtCore.QEventLoop, "ExcludeUserInputEvents")
        )

    def _text(self, key, **values):
        return ui_text.text(key, self.ui_language, **values)
