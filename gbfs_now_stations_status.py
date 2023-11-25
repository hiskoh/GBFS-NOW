import os,requests, json ,datetime

from qgis.core import *
from qgis.PyQt.QtCore import QVariant

STATION_PNG_PATH = os.path.join(os.path.dirname(__file__),  "station_now.png")

#ステーション ステータス情報を表示
def create_gbfs_station_now_layer(self,url):
    
    #データを取得
    url = requests.get(url)
    text = url.text
    data = json.loads(text)
    stations = data['data']['stations']
    
    
    #create qgisVectorLayer
    layer = QgsVectorLayer("Point", self.system_name + "_stations_status_now", "memory")
    
    # Start of the edition 
    layer.startEditing()
    
    #カラムを作成        
    layer.dataProvider().addAttributes( [
        QgsField('station_id'            , QVariant.String), 
        QgsField('name'                  , QVariant.String), 
        QgsField('capacity'              , QVariant.Int), 
        QgsField('num_bikes_available'   , QVariant.Int),
        QgsField('num_docks_available'   , QVariant.Int),
        QgsField('num_bikes_disabled'    , QVariant.Int),
        QgsField('is_renting'            , QVariant.Bool),
        QgsField('is_returning'          , QVariant.Bool),
        QgsField('last_reported'         , QVariant.String)
        ] )
    
    
    #update
    layer.updateFields()
    
    # Addition of features
    for station in stations:
        station_id = station['station_id']
        num_bikes_available = station['num_bikes_available']
        
        #ステーション情報から追加要素を取得
        for station_info in self.stations_info:
            if station_id == station_info['station_id']:
                name= station_info['name']     if 'name'     in station_info else None
                capa= station_info['capacity'] if 'capacity' in station_info else None
                lon = station_info['lon']      if 'lon'      in station_info else None
                lat = station_info['lat']      if 'lat'      in station_info else None
                
                
        f = QgsFeature()
        f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(lon,lat)))
        
        feature = []
        
        feature.append(station_id)
        feature.append(name)
        feature.append(capa)
        feature.append(station['num_bikes_available'] if 'num_bikes_available' in station else None)
        feature.append(station['num_docks_available'] if 'num_docks_available' in station else None)
        feature.append(station['num_bikes_disabled']  if 'num_bikes_disabled'  in station else None)
        feature.append(station['is_renting']          if 'is_renting'          in station else None)
        feature.append(station['is_returning']        if 'is_returning'        in station else None)
        
        last_reported = datetime.datetime.fromtimestamp(station['last_reported'] if 'last_reported' in station else None,datetime.timezone(datetime.timedelta(hours=9)))
        feature.append(str(last_reported))
        
        f.setAttributes(feature)
        layer.addFeature(f)            
    
    # saving changes and adding the layer
    layer.updateExtents() 
    
    #set layer symbol
    symbol = QgsRasterMarkerSymbolLayer(STATION_PNG_PATH)
    symbol.setSize(5)
    layer.renderer().symbol().changeSymbolLayer(0, symbol )

    layer.commitChanges()
    QgsProject.instance().addMapLayer(layer)


#ステーション ステータス情報を表示（jpStyle）
def create_gbfs_station_now_layer_jp(self,url):
    
    #データを取得
    url = requests.get(url)
    text = url.text
    data = json.loads(text)
    stations = data['data']['stations']
    
    
    #create qgisVectorLayer
    layer = QgsVectorLayer("Point", self.system_name + "_stations_status_now", "memory")
    
    # Start of the edition 
    layer.startEditing()
    
    #カラムを作成        
    layer.dataProvider().addAttributes( [
        QgsField('ステーションID'            , QVariant.String), 
        QgsField('ステーション名'                  , QVariant.String), 
        QgsField('最大駐輪可能台数（ラック数）'              , QVariant.Int), 
        QgsField('貸出可能台数'   , QVariant.Int),
        QgsField('返却可能台数'   , QVariant.Int),
        QgsField('駐輪不可ラック数'    , QVariant.Int),
        QgsField('貸出可能時間'            , QVariant.Bool),
        QgsField('返却可能時間'          , QVariant.Bool),
        QgsField('データ更新時間'         , QVariant.String)
        ] )
    
    
    #update
    layer.updateFields()
    
    # Addition of features
    for station in stations:
        station_id = station['station_id']
        num_bikes_available = station['num_bikes_available']
        
        #ステーション情報から追加要素を取得
        for station_info in self.stations_info:
            if station_id == station_info['station_id']:
                name= station_info['name']     if 'name'     in station_info else None
                capa= station_info['capacity'] if 'capacity' in station_info else None
                lon = station_info['lon']      if 'lon'      in station_info else None
                lat = station_info['lat']      if 'lat'      in station_info else None
                
                
        f = QgsFeature()
        f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(lon,lat)))
        
        feature = []
        
        feature.append(station_id)
        feature.append(name)
        feature.append(capa)
        feature.append(station['num_bikes_available'] if 'num_bikes_available' in station else None)
        feature.append(station['num_docks_available'] if 'num_docks_available' in station else None)
        feature.append(station['num_bikes_disabled']  if 'num_bikes_disabled'  in station else None)
        feature.append(station['is_renting']          if 'is_renting'          in station else None)
        feature.append(station['is_returning']        if 'is_returning'        in station else None)
        
        last_reported = datetime.datetime.fromtimestamp(station['last_reported'] if 'last_reported' in station else None,datetime.timezone(datetime.timedelta(hours=9)))
        feature.append(str(last_reported))
        
        f.setAttributes(feature)
        layer.addFeature(f)            
    
    # saving changes and adding the layer
    layer.updateExtents() 

    #set layer symbol
    symbol = QgsRasterMarkerSymbolLayer(STATION_PNG_PATH)
    symbol.setSize(5)
    layer.renderer().symbol().changeSymbolLayer(0, symbol )

    layer.commitChanges()
    QgsProject.instance().addMapLayer(layer)
