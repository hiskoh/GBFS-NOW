import os
import requests, json 
import pandas as pd

from qgis.core import *
from qgis.PyQt import QtGui, QtWidgets, uic
from qgis.PyQt.QtCore import pyqtSignal
from qgis.PyQt.QtCore import QVariant
from qgis.PyQt.QtCore import QSortFilterProxyModel

from . import table_model

class gbfs_now_search_Dialog(QtWidgets.QDialog):
    
    def __init__(self, parent):
        
        super().__init__(parent)
        
        
        self.ui_s = uic.loadUi(os.path.join(os.path.dirname(__file__), 'gbfs_now_search_dialog.ui'), self) 
        self.ui_s.show()
        
        #GBFSリスト検索→表示
        self.get_gbfs_list()
        
    def get_gbfs_list(self):
        
        
        #Github repository
        url = 'https://raw.githubusercontent.com/MobilityData/gbfs/master/systems.csv'
        
        #get gbfs_list
        try:
            df = pd.read_csv(url, quotechar='"', skipinitialspace=True, error_bad_lines=False, warn_bad_lines=True)
        except Exception as e:
            print("エラーが発生しました:", e)
        
        #TableView更新
        model = table_model.createTableModel(df.values.tolist(), ["Country Code","Name","Location","System ID","URL","Auto-Discovery URL","Authentication Info"])
        #self.gbfs_list.setModel(model)
        
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setFilterKeyColumn(-1)
        self.proxy_model.setSourceModel(model)
        self.gbfs_list.setModel(self.proxy_model)
        
        #searchbar
        self.searchbar.textChanged.connect(self.proxy_model.setFilterFixedString)
        
        #search bar---
        

    def get_url(self):
        
        gbfs_url = None
        result = self.exec()
        
        if self.gbfs_list.selectionModel() and self.gbfs_list.selectionModel().hasSelection():
            row_num  = self.gbfs_list.selectionModel().selectedRows()[0].row()
            gbfs_url = self.gbfs_list.model().index(row_num,5).data()
            
        return (gbfs_url, result == QtWidgets.QDialog.Accepted)