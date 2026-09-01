# -*- coding: utf-8 -*-

import os

from qgis.PyQt import QtWidgets, uic
from qgis.PyQt.QtCore import QSettings, QSortFilterProxyModel, Qt

from .gbfs_now_core.catalog import CatalogError, fetch_systems_catalog
from .gbfs_now_core.qt_compat import class_enum, compatible_qt


Qt = compatible_qt(Qt)
from .gbfs_now_core.table_models import ListTableModel
from .gbfs_now_core import ui_text


class gbfs_now_search_Dialog(QtWidgets.QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(__file__), "gbfs_now_search_dialog.ui"), self)
        self.ui_language = ui_text.language_for_locale(
            QSettings().value("locale/userLocale", "")
        )
        self.proxy_model = QSortFilterProxyModel(self)
        self.url_column = 5
        self._configure_ui()
        self._load_catalog()

    def get_url(self):
        result = self.exec()
        if result != class_enum(QtWidgets.QDialog, "Accepted"):
            return None, False

        selection_model = self.gbfs_list.selectionModel()
        if not selection_model or not selection_model.hasSelection():
            return None, True

        selected_row = selection_model.selectedRows()[0].row()
        gbfs_url = self.gbfs_list.model().index(selected_row, self.url_column).data()
        return gbfs_url, True

    def _configure_ui(self):
        self.setWindowTitle(self._text("catalog_title"))
        self.label.setText(self._text("select_gbfs_system"))
        self.label_2.setText(self._text("catalog_source"))
        self.label_3.setText(self._text("search_label"))
        self.searchbar.setPlaceholderText(self._text("search_catalog_placeholder"))
        self.proxy_model.setFilterKeyColumn(-1)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.gbfs_list.setModel(self.proxy_model)
        self.gbfs_list.setSelectionBehavior(
            class_enum(QtWidgets.QAbstractItemView, "SelectRows")
        )
        self.gbfs_list.setSelectionMode(
            class_enum(QtWidgets.QAbstractItemView, "SingleSelection")
        )
        self.gbfs_list.setEditTriggers(
            class_enum(QtWidgets.QAbstractItemView, "NoEditTriggers")
        )
        self.gbfs_list.setSortingEnabled(True)
        self.gbfs_list.doubleClicked.connect(self.accept)
        self.searchbar.textChanged.connect(self.proxy_model.setFilterFixedString)

    def _load_catalog(self):
        try:
            headers, rows = fetch_systems_catalog()
        except CatalogError as error:
            QtWidgets.QMessageBox.warning(
                self, "GBFS-NOW", self._text("catalog_load_error", error=error)
            )
            headers, rows = [], []

        self.url_column = headers.index("Auto-Discovery URL") if "Auto-Discovery URL" in headers else 5
        model = ListTableModel(rows, headers, self)
        self.proxy_model.setSourceModel(model)
        self.gbfs_list.resizeColumnsToContents()
        if rows and len(headers) > 1:
            self.gbfs_list.sortByColumn(1, Qt.AscendingOrder)

    def _text(self, key, **values):
        return ui_text.text(key, self.ui_language, **values)
