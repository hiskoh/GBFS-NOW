# -*- coding: utf-8 -*-

import os

from qgis.PyQt.QtCore import QCoreApplication, QSettings, QTranslator, Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

from . import resources
from .gbfs_now_core.catalog import prefetch_systems_catalog
from .gbfs_now_core.qt_compat import compatible_qt
from .gbfs_now_dockwidget import gbfs_nowDockWidget


Qt = compatible_qt(Qt)


class gbfs_now:
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.translator = None
        self.actions = []
        self.menu = self.tr("&GBFS-NOW")
        self.toolbar = self.iface.addToolBar("gbfs_now")
        self.toolbar.setObjectName("gbfs_now")
        self.pluginIsActive = False
        self.dockwidget = None
        self._install_translator()
        prefetch_systems_catalog()

    def tr(self, message):
        return QCoreApplication.translate("gbfs_now", message)

    def initGui(self):
        action = QAction(
            QIcon(":/plugins/gbfs_now/icon.png"),
            self.tr("GBFS-NOW"),
            self.iface.mainWindow(),
        )
        action.triggered.connect(self.run)
        self.toolbar.addAction(action)
        self.iface.addPluginToWebMenu(self.menu, action)
        self.actions.append(action)

    def unload(self):
        for action in self.actions:
            self.iface.removePluginWebMenu(self.menu, action)
            self.iface.removeToolBarIcon(action)
        del self.toolbar

    def run(self):
        if not self.pluginIsActive:
            self.pluginIsActive = True
            if self.dockwidget is None:
                self.dockwidget = gbfs_nowDockWidget()
            self.dockwidget.closingPlugin.connect(self.onClosePlugin)
            self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dockwidget)
        self.dockwidget.show()

    def onClosePlugin(self):
        try:
            self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)
        except TypeError:
            pass
        self.pluginIsActive = False

    def _install_translator(self):
        locale = str(QSettings().value("locale/userLocale", ""))[:2]
        locale_path = os.path.join(self.plugin_dir, "i18n", "gbfs_now_{}.qm".format(locale))
        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)
