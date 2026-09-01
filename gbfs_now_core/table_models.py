# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import QAbstractTableModel, Qt, QUrl
from qgis.PyQt.QtGui import QIcon, QPixmap
from qgis.PyQt.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest

from . import compat
from .qt_compat import enum_value, network_reply_no_error




class ListTableModel(QAbstractTableModel):
    def __init__(self, rows, headers=None, parent=None):
        super().__init__(parent)
        self.rows = rows or []
        self.headers = headers or []

    def rowCount(self, parent=None):
        return len(self.rows)

    def columnCount(self, parent=None):
        return len(self.headers) or max((len(row) for row in self.rows), default=0)

    def flags(self, index):
        if not index.isValid():
            return enum_value(Qt, "ItemFlag", "NoItemFlags")
        return enum_value(Qt, "ItemFlag", "ItemIsEnabled") | enum_value(
            Qt, "ItemFlag", "ItemIsSelectable"
        )

    def data(self, index, role):
        if not index.isValid() or role not in (
            enum_value(Qt, "ItemDataRole", "DisplayRole"),
            enum_value(Qt, "ItemDataRole", "EditRole"),
        ):
            return None
        row = index.row()
        column = index.column()
        if row >= len(self.rows) or column >= len(self.rows[row]):
            return None
        return self.rows[row][column]

    def headerData(self, section, orientation, role):
        if role != enum_value(Qt, "ItemDataRole", "DisplayRole"):
            return None
        if orientation == enum_value(Qt, "Orientation", "Horizontal"):
            if section < len(self.headers):
                return self.headers[section]
            return ""
        return str(section + 1)


class VehicleTypesTableModel(QAbstractTableModel):
    def __init__(self, records, language=None, fallback_icon=None, parent=None):
        super().__init__(parent)
        self.records = records or []
        self.language = language
        self.fallback_icon = fallback_icon
        self.headers = []
        self.rows = []
        self.icon_urls = []
        self.vehicle_images = []
        self.image_cache = {}
        self.manager = QNetworkAccessManager()
        self.manager.finished.connect(self.on_download_finished)
        self._prepare()

    def _prepare(self):
        for item in self.records:
            for key in item.keys():
                if key not in ("vehicle_assets", "vehicle_image") and key not in self.headers:
                    self.headers.append(key)

        rows = []
        for key in self.headers:
            rows.append(
                [compat.display_value(item.get(key), self.language) for item in self.records]
            )
        self.rows = rows

        self.icon_urls = [
            item.get("vehicle_assets", {}).get("icon_url")
            if isinstance(item.get("vehicle_assets"), dict) else None
            for item in self.records
        ]
        self.vehicle_images = [item.get("vehicle_image") for item in self.records]

        for image_url in self.icon_urls + self.vehicle_images:
            if image_url:
                self._request_image(image_url)

    def _request_image(self, image_url):
        request = QNetworkRequest(QUrl(image_url))
        redirect_attribute = getattr(QNetworkRequest, "RedirectPolicyAttribute", None)
        redirect_policy = getattr(QNetworkRequest, "NoLessSafeRedirectPolicy", None)
        if redirect_attribute is None:
            redirect_attribute = getattr(
                getattr(QNetworkRequest, "Attribute", None),
                "RedirectPolicyAttribute",
                None,
            )
        if redirect_policy is None:
            redirect_policy = getattr(
                getattr(QNetworkRequest, "RedirectPolicy", None),
                "NoLessSafeRedirectPolicy",
                None,
            )
        if redirect_attribute is not None and redirect_policy is not None:
            request.setAttribute(redirect_attribute, redirect_policy)
        elif hasattr(QNetworkRequest, "FollowRedirectsAttribute"):
            request.setAttribute(QNetworkRequest.FollowRedirectsAttribute, True)
        self.manager.get(request)

    def rowCount(self, parent=None):
        extra_rows = 0
        if any(self.icon_urls):
            extra_rows += 1
        if any(self.vehicle_images):
            extra_rows += 1
        return len(self.headers) + extra_rows

    def columnCount(self, parent=None):
        return len(self.records)

    def data(self, index, role):
        if not index.isValid():
            return None

        if role == enum_value(Qt, "ItemDataRole", "DisplayRole"):
            if 0 <= index.row() < len(self.rows):
                row = self.rows[index.row()]
                if 0 <= index.column() < len(row):
                    return row[index.column()]

        if role == enum_value(Qt, "ItemDataRole", "DecorationRole"):
            image_url = self._image_url_for(index.row(), index.column())
            if image_url:
                return self.image_cache.get(image_url)

        return None

    def _image_url_for(self, row, column):
        icon_row = len(self.headers)
        vehicle_image_row = icon_row + (1 if any(self.icon_urls) else 0)
        if any(self.icon_urls) and row == icon_row and column < len(self.icon_urls):
            return self.icon_urls[column]
        if (
            any(self.vehicle_images)
            and row == vehicle_image_row
            and column < len(self.vehicle_images)
        ):
            return self.vehicle_images[column]
        return None

    def headerData(self, section, orientation, role):
        if role != enum_value(Qt, "ItemDataRole", "DisplayRole"):
            return None
        if orientation == enum_value(Qt, "Orientation", "Horizontal"):
            return "vehicle {}".format(section + 1)
        if section < len(self.headers):
            return self.headers[section]
        if any(self.icon_urls) and section == len(self.headers):
            return "icon"
        if any(self.vehicle_images):
            image_row = len(self.headers) + (1 if any(self.icon_urls) else 0)
            if section == image_row:
                return "vehicle_image"
        return None

    def clear(self):
        self.beginResetModel()
        self.records = []
        self.headers = []
        self.rows = []
        self.icon_urls = []
        self.vehicle_images = []
        self.image_cache = {}
        self.endResetModel()

    def on_download_finished(self, reply):
        url = reply.request().url().toString()
        if reply.error() == network_reply_no_error(QNetworkReply):
            pixmap = QPixmap()
            pixmap.loadFromData(reply.readAll())
            self.image_cache[url] = QIcon(
                pixmap.scaled(220, 220, enum_value(Qt, "AspectRatioMode", "KeepAspectRatio"))
            )
        elif self.fallback_icon:
            self.image_cache[url] = QIcon(self.fallback_icon)

        if self.rowCount() and self.columnCount():
            top_left = self.index(0, 0)
            bottom_right = self.index(self.rowCount() - 1, self.columnCount() - 1)
            self.dataChanged.emit(
                top_left,
                bottom_right,
                [enum_value(Qt, "ItemDataRole", "DecorationRole")],
            )
        reply.deleteLater()
