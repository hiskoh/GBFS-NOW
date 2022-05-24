import os
import requests, json 
import pandas as pd

from qgis.core import *
from qgis.PyQt import QtGui, QtWidgets, uic
from qgis.PyQt.QtCore import pyqtSignal
from qgis.PyQt.QtCore import QVariant

from . import table_model

class gbfs_now_search_Dialog(QtWidgets.QDialog):
    
    def __init__(self, parent):
        
        super().__init__(parent)
        
        
        self.ui_s = uic.loadUi(os.path.join(os.path.dirname(__file__), 'gbfs_now_search_dialog.ui'), self) 
        self.ui_s.show()
        
        #GBFSリスト検索→表示
        self.get_gbfs_list()
        self.get_gbfs_button.clicked.connect(self.get_gbfs_list) 
        
        
    def get_gbfs_list(self):
        
        
        #get data
        url = self.gbfs_list_url.text()
        df = pd.read_csv(url)
        
        #TableView更新
        model = table_model.createTableModel(df.values.tolist(), ["Country Code","Name","Location","System ID","URL","Auto-Discovery URL"])
        self.gbfs_list.setModel(model)
        

    def get_url(self):
        
        gbfs_url = None
        result = self.exec()
        
        if self.gbfs_list.selectionModel() and self.gbfs_list.selectionModel().hasSelection():
            row_num  = self.gbfs_list.selectionModel().selectedRows()[0].row()
            gbfs_url = self.gbfs_list.model().index(row_num,5).data()
            
        return (gbfs_url, result == QtWidgets.QDialog.Accepted)