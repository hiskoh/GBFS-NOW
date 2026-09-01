# -*- coding: utf-8 -*-

import json
import os

from qgis.PyQt.QtCore import QVariant
from qgis.core import (
    QgsFeature,
    QgsField,
    QgsGeometry,
    QgsPointXY,
    QgsProject,
    QgsRasterMarkerSymbolLayer,
    QgsVectorLayer,
)

try:
    from qgis.core import Qgis, QgsMessageLog
except ImportError:
    Qgis = None
    QgsMessageLog = None

from . import compat
from .labels import field_label
from .qt_compat import qgis_message_level


STATION_FIELDS = [
    ("station_id", QVariant.String, ["station_id"]),
    ("name", QVariant.String, ["name"]),
    ("short_name", QVariant.String, ["short_name"]),
    (
        "capacity",
        QVariant.Int,
        [
            "capacity",
            "vehicle_docks_capacity",
            "vehicle_types_capacity",
            "vehicle_capacity",
            "vehicle_type_capacity",
        ],
    ),
    ("address", QVariant.String, ["address"]),
    ("cross_street", QVariant.String, ["cross_street"]),
    ("region_id", QVariant.String, ["region_id"]),
    ("post_code", QVariant.String, ["post_code"]),
    ("rental_methods", QVariant.String, ["rental_methods"]),
    ("is_virtual_station", QVariant.Bool, ["is_virtual_station"]),
    ("parking_type", QVariant.String, ["parking_type"]),
    ("parking_hoop", QVariant.Bool, ["parking_hoop"]),
    ("contact_phone", QVariant.String, ["contact_phone", "contact_phone "]),
    ("vehicle_types_capacity", QVariant.String, ["vehicle_types_capacity", "vehicle_capacity"],),
    ("vehicle_docks_capacity", QVariant.String, ["vehicle_docks_capacity", "vehicle_type_capacity"],),
    ("is_valet_station", QVariant.Bool, ["is_valet_station"]),
    ("is_charging_station", QVariant.Bool, ["is_charging_station"]),
    ("android", QVariant.String, ["rental_uris.android", "android"]),
    ("ios", QVariant.String, ["rental_uris.ios", "ios", "ios "]),
    ("web", QVariant.String, ["rental_uris.web", "web"]),
    ("lon", QVariant.Double, ["lon", "longitude"]),
    ("lat", QVariant.Double, ["lat", "latitude"]),
]

STATION_STATUS_FIELDS = [
    ("station_id", QVariant.String, ["station_id"]),
    ("name", QVariant.String, ["station_information.name"]),
    (
        "capacity",
        QVariant.Int,
        [
            "station_information.capacity",
            "station_information.vehicle_docks_capacity",
            "station_information.vehicle_types_capacity",
            "station_information.vehicle_capacity",
            "station_information.vehicle_type_capacity",
        ],
    ),
    ("num_vehicles_available", QVariant.Int, ["num_vehicles_available", "num_bikes_available"]),
    ("num_docks_available", QVariant.Int, ["num_docks_available"]),
    ("num_vehicles_disabled", QVariant.Int, ["num_vehicles_disabled", "num_bikes_disabled"]),
    ("num_docks_disabled", QVariant.Int, ["num_docks_disabled"]),
    ("is_installed", QVariant.Bool, ["is_installed"]),
    ("is_renting", QVariant.Bool, ["is_renting"]),
    ("is_returning", QVariant.Bool, ["is_returning"]),
    ("vehicle_types_available", QVariant.String, ["vehicle_types_available"]),
    ("vehicle_docks_available", QVariant.String, ["vehicle_docks_available"]),
    ("last_reported", QVariant.String, ["last_reported"]),
]

VEHICLE_FIELDS = [
    ("vehicle_id", QVariant.String, ["vehicle_id", "bike_id"]),
    ("is_reserved", QVariant.Bool, ["is_reserved"]),
    ("is_disabled", QVariant.Bool, ["is_disabled"]),
    ("vehicle_type_id", QVariant.String, ["vehicle_type_id"]),
    ("last_reported", QVariant.String, ["last_reported"]),
    ("current_range_meters", QVariant.String, ["current_range_meters"]),
    ("current_fuel_percent", QVariant.String, ["current_fuel_percent"]),
    ("station_id", QVariant.String, ["station_id"]),
    ("home_station_id", QVariant.String, ["home_station_id"]),
    ("pricing_plan_id", QVariant.String, ["pricing_plan_id"]),
    ("vehicle_equipment", QVariant.String, ["vehicle_equipment"]),
    ("available_until", QVariant.String, ["available_until"]),
    ("android", QVariant.String, ["rental_uris.android", "android"]),
    ("ios", QVariant.String, ["rental_uris.ios", "ios", "ios "]),
    ("web", QVariant.String, ["rental_uris.web", "web"]),
    ("lon", QVariant.Double, ["lon"]),
    ("lat", QVariant.Double, ["lat"]),
]


class LayerBuilder:
    def __init__(self, plugin_dir):
        self.plugin_dir = plugin_dir
        self.replace_existing = True

    def add_stations(self, system_name, station_feed, language, label_language):
        stations = compat.records(station_feed, "stations")
        layer = self._point_layer(
            "{}_stations".format(system_name),
            "station",
            STATION_FIELDS,
            stations,
            language,
            label_language,
            lambda station: self._coordinates(station),
            self._icon_path("station.png"),
        )
        self._add_layer(layer)
        return stations

    def add_station_status(self, system_name, status_feed, stations, language, label_language):
        station_index = self.station_index(stations)
        status_records = compat.records(status_feed, "stations")
        joined_records = []
        for status in status_records:
            station = station_index.get(status.get("station_id"), {})
            joined = dict(status)
            joined["station_information"] = station
            joined_records.append(joined)

        layer = self._point_layer(
            "{}_stations_status_now".format(system_name),
            "station_status",
            STATION_STATUS_FIELDS,
            joined_records,
            language,
            label_language,
            lambda status: self._coordinates(status.get("station_information", {})),
            self._icon_path("station_now.png"),
        )
        self._add_layer(layer)

    def add_vehicles(self, system_name, vehicle_feed, stations, language, label_language):
        station_index = self.station_index(stations)
        vehicles = compat.records(vehicle_feed, "vehicles", "bikes")

        layer = self._point_layer(
            "{}_vehicles".format(system_name),
            "vehicle",
            VEHICLE_FIELDS,
            vehicles,
            language,
            label_language,
            lambda vehicle: self._vehicle_coordinates(vehicle, station_index),
            self._icon_path("bike.png"),
        )
        self._add_layer(layer)

    @staticmethod
    def station_index(stations):
        return {
            station.get("station_id"): station
            for station in stations
            if isinstance(station, dict) and station.get("station_id") is not None
        }

    def _point_layer(
        self,
        name,
        label_group,
        field_specs,
        records,
        language,
        label_language,
        coordinates,
        icon_path,
    ):
        layer = QgsVectorLayer("Point?crs=EPSG:4326", self._layer_name(name), "memory")
        provider = layer.dataProvider()
        provider.addAttributes(
            [
                QgsField(field_label(label_group, key, label_language), field_type)
                for key, field_type, paths in field_specs
            ]
        )
        layer.updateFields()

        features = []
        skipped = 0
        for record in records:
            lon, lat = coordinates(record)
            if not self._valid_coordinates(lon, lat):
                skipped += 1
                continue

            feature = QgsFeature(layer.fields())
            feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(lon, lat)))
            feature.setAttributes(
                [
                    self._field_value(record, key, paths, language, field_type)
                    for key, field_type, paths in field_specs
                ]
            )
            features.append(feature)

        added = self._add_features(provider, features)
        layer.updateExtents()
        self._set_icon(layer, icon_path)
        self._log_layer_result(name, len(records), len(features), added, skipped)
        return layer

    @staticmethod
    def _field_value(record, key, paths, language, field_type):
        if key == "last_reported":
            value = compat.format_timestamp(compat.field_value(record, paths[0], language))
            return LayerBuilder._qgis_value(value, field_type)
        if key == "capacity":
            return LayerBuilder._qgis_value(
                LayerBuilder._capacity_value(record, paths), field_type
            )
        for path in paths:
            value = compat.field_value(record, path, language)
            if value is not None:
                return LayerBuilder._qgis_value(value, field_type)
        return None

    @staticmethod
    def _qgis_value(value, field_type):
        if value is None:
            return None
        if field_type == QVariant.String:
            if isinstance(value, (dict, list, tuple)):
                return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
            return str(value)
        if field_type == QVariant.Int:
            number = LayerBuilder._capacity_total(value)
            return number if number is not None else None
        if field_type == QVariant.Double:
            return compat.as_float(value)
        if field_type == QVariant.Bool:
            return bool(value)
        return value

    @staticmethod
    def _valid_coordinates(lon, lat):
        return (
            lon is not None
            and lat is not None
            and -180 <= lon <= 180
            and -90 <= lat <= 90
        )

    @staticmethod
    def _add_features(provider, features):
        if not features:
            return 0
        result = provider.addFeatures(features)
        if LayerBuilder._add_features_succeeded(result):
            return len(features)

        added = 0
        for feature in features:
            if LayerBuilder._add_features_succeeded(provider.addFeatures([feature])):
                added += 1
        return added

    @staticmethod
    def _add_features_succeeded(result):
        if isinstance(result, tuple):
            return bool(result[0])
        return bool(result)

    @staticmethod
    def _log_layer_result(name, total, candidates, added, skipped):
        if QgsMessageLog is None:
            return
        message = "{}: {} records, {} coordinates, {} added".format(
            name, total, candidates, added
        )
        if skipped:
            message += ", {} skipped without valid coordinates".format(skipped)
        level = qgis_message_level(
            Qgis, "Warning" if added != candidates and Qgis is not None else "Info"
        )
        QgsMessageLog.logMessage(message, "GBFS-NOW", level)

    @staticmethod
    def _coordinates(record):
        lon = compat.as_float(
            compat.field_value(record, "lon", fallback_keys=["longitude"])
        )
        lat = compat.as_float(
            compat.field_value(record, "lat", fallback_keys=["latitude"])
        )
        if lon is None or lat is None:
            return LayerBuilder._area_coordinates(record)
        return lon, lat

    @staticmethod
    def _capacity_value(record, paths):
        for path in paths:
            value, found = compat.nested_value(record, path)
            if not found or value in (None, ""):
                continue
            capacity = LayerBuilder._capacity_total(value)
            if capacity is not None:
                return capacity
        return None

    @staticmethod
    def _capacity_total(value):
        if isinstance(value, bool):
            return None
        if isinstance(value, (int, float)):
            return int(value)
        if isinstance(value, str):
            try:
                return int(float(value))
            except ValueError:
                return None
        if isinstance(value, dict):
            total = 0
            found = False
            for item in value.values():
                number = LayerBuilder._capacity_total(item)
                if number is not None:
                    total += number
                    found = True
            return total if found else None
        if isinstance(value, list):
            total = 0
            found = False
            for item in value:
                if isinstance(item, dict) and "count" in item:
                    number = LayerBuilder._capacity_total(item.get("count"))
                else:
                    number = None
                if number is not None:
                    total += number
                    found = True
            return total if found else None
        return None

    @staticmethod
    def _area_coordinates(record):
        station_area = record.get("station_area")
        coordinates = None
        if isinstance(station_area, dict):
            coordinates = station_area.get("coordinates")
        elif station_area is not None:
            coordinates = station_area
        if coordinates is None:
            coordinates = record.get("coordinates")

        pairs = []
        LayerBuilder._collect_coordinate_pairs(coordinates, pairs)
        if not pairs:
            return None, None
        lon = sum(pair[0] for pair in pairs) / len(pairs)
        lat = sum(pair[1] for pair in pairs) / len(pairs)
        return lon, lat

    @staticmethod
    def _collect_coordinate_pairs(value, pairs):
        if not isinstance(value, (list, tuple)):
            return
        if len(value) >= 2:
            lon = compat.as_float(value[0])
            lat = compat.as_float(value[1])
            if lon is not None and lat is not None:
                pairs.append((lon, lat))
                return
        for item in value:
            LayerBuilder._collect_coordinate_pairs(item, pairs)

    def _vehicle_coordinates(self, vehicle, station_index):
        lon, lat = self._coordinates(vehicle)
        if lon is not None and lat is not None:
            return lon, lat
        station = station_index.get(vehicle.get("station_id"), {})
        return self._coordinates(station)

    def _icon_path(self, filename):
        return os.path.join(self.plugin_dir, filename)

    @staticmethod
    def _layer_name(name):
        return " ".join(str(name or "GBFS").split())[:120]

    @staticmethod
    def _set_icon(layer, icon_path):
        if not os.path.exists(icon_path):
            return
        symbol_layer = QgsRasterMarkerSymbolLayer(icon_path)
        symbol_layer.setSize(5)
        layer.renderer().symbol().changeSymbolLayer(0, symbol_layer)

    def _add_layer(self, layer):
        project = QgsProject.instance()
        if self.replace_existing:
            for existing_layer in self._layers_by_name(project, self._qgis_layer_name(layer)):
                if hasattr(existing_layer, "id") and hasattr(project, "removeMapLayer"):
                    project.removeMapLayer(existing_layer.id())
        project.addMapLayer(layer)

    @staticmethod
    def _qgis_layer_name(layer):
        name = getattr(layer, "name", None)
        return name() if callable(name) else name

    @staticmethod
    def _layers_by_name(project, name):
        if not name:
            return []
        if hasattr(project, "mapLayersByName"):
            return project.mapLayersByName(name)
        return []
