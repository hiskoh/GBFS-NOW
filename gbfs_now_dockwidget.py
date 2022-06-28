# -*- coding: utf-8 -*-
"""
/***************************************************************************
 gbfs_nowDockWidget
                                 A QGIS plugin
 view gbfs-data
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2022-05-21
        git sha              : $Format:%H$
        copyright            : (C) 2022 by Kohta Hisadomi
        email                : his.koh3.biz@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os
import requests, json

from qgis.PyQt import QtGui, QtWidgets, uic
from qgis.PyQt.QtCore import pyqtSignal
from qgis.PyQt.QtCore import QVariant


from . import gbfs_now_system_info as nSys
from . import gbfs_now_stations as nSta
from . import gbfs_now_stations_status as nSta_now
from . import gbfs_now_search_dialog as nSch
from . import table_model

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'gbfs_now_dockwidget_base.ui'))

class gbfs_nowDockWidget(QtWidgets.QDockWidget, FORM_CLASS):

    closingPlugin = pyqtSignal()

    def __init__(self, parent=None):
        """Constructor."""
        super(gbfs_nowDockWidget, self).__init__(parent)
        self.setupUi(self)
        
        #gbfsデータ格納用
        self.gbfs_json_data = None
        
        #Toolボタン選択→GBFSカタログ
        self.toolButton.clicked.connect(self.show_search_dialog)
        
        #GBFS検索→表示
        self.searchButton.clicked.connect(self.search_gbfs_dataset) 
        self.viewButton.clicked.connect(self.view_gbfs_dataset)
        

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()
        
        
    #GBFS Listの検索
    def show_search_dialog(self):
        text , result = nSch.gbfs_now_search_Dialog(self).get_url()  
        self.gbfs_url.setText(text)
        
    #GBFSデータの検索
    def search_gbfs_dataset(self):
        
        
        #画面入力URLを取得
        gbfs_json = self.gbfs_url.text()
        
        #gbfs.json requests
        try:
            response = requests.get(gbfs_json)
            response.raise_for_status()
            
        except requests.exceptions.RequestException:
            contents = [["No data... Check the url."]]
        else:
            text = response.text
            data = json.loads(text)
            
            self.gbfs_json_data = data["data"]
            contents = [[language] for language in data["data"].keys()]
            
            #初期値として保存
            self.gbfs_language = list(data["data"].keys())[0]
        
        #検索結果欄の更新
        model = table_model.createTableModel(contents, ["data list"])
        self.gbfs_datalist.setModel(model)
        
        
    

    #GBFSデータの表示
    def view_gbfs_dataset(self):
        
        if self.gbfs_json_data == None:
            nSys.clear_gbfs_system_info_viewer(self)
            return
        
        #表示したい言語（選択した言語）の取得
        if self.gbfs_datalist.selectionModel().hasSelection():
            self.gbfs_language = self.gbfs_datalist.selectionModel().selectedRows()[0].data()
        
        
        #system情報の表示
        gbfs_system_info_url = self.get_gbfs_each_url('system_information')
        nSys.create_gbfs_system_info_viewer(self,gbfs_system_info_url)
        
        #ステーションレイヤの表示
        station_info_url = self.get_gbfs_each_url('station_information')
        
        if station_info_url != None:
            if self.jpStyle.isChecked():
                nSta.create_gbfs_station_layer_jp(self,station_info_url)         	
            else:
                nSta.create_gbfs_station_layer(self,station_info_url) 
        
        #ステーション現況レイヤの表示
        if self.station_now_button.isChecked():
            station_status_url = self.get_gbfs_each_url('station_status')
            
            if station_status_url != None and self.jpStyle.isChecked():
                nSta_now.create_gbfs_station_now_layer_jp(self,station_status_url)
            elif station_status_url != None and not self.jpStyle.isChecked():
                nSta_now.create_gbfs_station_now_layer(self,station_status_url)
            
    #gbfs.jsonからgbfs構成jsonのURLを取得
    def get_gbfs_each_url(self,filename):
        feeds = self.gbfs_json_data[self.gbfs_language]["feeds"]
        item = next((item for item in feeds if item['name'] == filename), None)
        file_url = item["url"] if item is not None else None
        return file_url
        