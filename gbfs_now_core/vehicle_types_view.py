# -*- coding: utf-8 -*-

import os

from .compat import records
from .table_models import VehicleTypesTableModel


def render(widget, vehicle_types_feed, language, plugin_dir):
    vehicle_types = records(vehicle_types_feed, "vehicle_types")
    fallback_icon = os.path.join(plugin_dir, "no_image.png")
    model = VehicleTypesTableModel(vehicle_types, language, fallback_icon)
    widget.vehicle_types_table.setModel(model)
    table = widget.vehicle_types_table

    table.resizeColumnsToContents()
    for row in range(model.rowCount()):
        table.resizeRowToContents(row)
    table.resizeRowsToContents()
    if any(model.icon_urls):
        table.setRowHeight(len(model.headers), 230)

    if any(model.vehicle_images):
        image_row = len(model.headers) + (1 if any(model.icon_urls) else 0)
        table.setRowHeight(image_row, 230)
    height = table.horizontalHeader().height() + table.frameWidth() * 2
    height += sum(table.rowHeight(row) for row in range(model.rowCount()))
    table.setFixedHeight(max(height, 1))


def clear(widget):
    if not hasattr(widget, "vehicle_types_table"):
        return
    model = widget.vehicle_types_table.model()
    if isinstance(model, VehicleTypesTableModel):
        model.clear()
    else:
        widget.vehicle_types_table.setModel(None)
