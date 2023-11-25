import os, requests, json

from qgis.core import *
from qgis.PyQt.QtCore import QVariant
STATION_PNG_PATH = os.path.join(os.path.dirname(__file__),  "station.png")


#ステーション情報を表示
def create_gbfs_station_layer(self,url):
    
    #ステーション情報取得
    response = requests.get(url)
    text = response.text
    data = json.loads(text)
    
    #station情報保持
    gbfs_stations = data["data"]["stations"]
    self.stations_info = gbfs_stations
    
    #create qgisVectorLayer
    layer = QgsVectorLayer("Point", self.system_name + "_stations", "memory")
    
    # Start of the edition 
    layer.startEditing()
    
    #カラムを作成        
    layer.dataProvider().addAttributes( [
        QgsField('station_id'            , QVariant.String), 
        QgsField('name'                  , QVariant.String), 
        QgsField('short_name'            , QVariant.String), 
        QgsField('capacity'              , QVariant.Int), 
        QgsField('address'               , QVariant.String), 
        QgsField('cross_street'          , QVariant.String), 
        QgsField('region_id'             , QVariant.String), 
        QgsField('post_code'             , QVariant.String), 
        QgsField('rental_methods'        , QVariant.String), 
        QgsField('is_virtual_station'    , QVariant.Bool),   
        #QgsField('station_area'          , QVariant.String), 
        QgsField('parking_type'          , QVariant.String), 
        QgsField('parking_hoop'          , QVariant.Bool),   
        QgsField('contact_phone '        , QVariant.String), 
        #QgsField('vehicle_capacity'      , QVariant.String), 
        QgsField('vehicle_type_capacity' , QVariant.String), 
        QgsField('is_valet_station'      , QVariant.Bool),   
        QgsField('is_charging_station'   , QVariant.Bool), 
        QgsField('android'               , QVariant.String), 
        QgsField('ios '                  , QVariant.String), 
        QgsField('web'                   , QVariant.String),  
        QgsField('lon'                   , QVariant.Double), 
        QgsField('lat'                   , QVariant.Double) 
        ] )
    
    
    #update
    layer.updateFields()
    
    # Addition of features
    for station in gbfs_stations:
        f = QgsFeature()
        f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(station["lon"],station["lat"])))
        
        feature = []
        
        feature.append(station['station_id'           ] if 'station_id'            in station else None)
        feature.append(station['name'                 ] if 'name'                  in station else None)
        feature.append(station['short_name'           ] if 'short_name'            in station else None)
        feature.append(station['capacity'             ] if 'capacity'              in station else None)
        feature.append(station['address'              ] if 'address'               in station else None)
        feature.append(station['cross_street'         ] if 'cross_street'          in station else None)
        feature.append(station['region_id'            ] if 'region_id'             in station else None)
        feature.append(station['post_code'            ] if 'post_code'             in station else None)
        feature.append(", ".join(station['rental_methods']) if 'rental_methods'    in station else None)
        feature.append(station['is_virtual_station'   ] if 'is_virtual_station'    in station else None)
        #feature.append(station['station_area'         ] if 'station_area'          in station else None)
        feature.append(station['parking_type'         ] if 'parking_type'          in station else None)
        feature.append(station['parking_hoop'         ] if 'parking_hoop'          in station else None)
        feature.append(station['contact_phone '       ] if 'contact_phone '        in station else None)
        #feature.append(station['vehicle_capacity'     ] if 'vehicle_capacity'      in station else None)
        feature.append('\n'.join([f"{key}: {value}" for key, value in station['vehicle_type_capacity'].items()]) if 'vehicle_type_capacity' in station else None)
        feature.append(station['is_valet_station'     ] if 'is_valet_station'      in station else None)
        feature.append(station['is_charging_station'  ] if 'is_charging_station'   in station else None)
        feature.append(station['android'              ] if 'android'               in station else None)
        feature.append(station['ios '                 ] if 'ios '                  in station else None)
        feature.append(station['web'                  ] if 'web'                   in station else None)
        feature.append(station['lon'                  ] if 'lon'                   in station else None)
        feature.append(station['lat'                  ] if 'lat'                   in station else None)
        
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

#ステーション情報を表示(jp-style)
def create_gbfs_station_layer_jp(self,url):

    #ステーション情報取得
    response = requests.get(url)
    text = response.text
    data = json.loads(text)
    
    #station情報保持
    gbfs_stations = data["data"]["stations"]
    self.stations_info = gbfs_stations
    
    #create qgisVectorLayer
    layer = QgsVectorLayer("Point", self.system_name + "_stations", "memory")
    
    # Start of the edition 
    layer.startEditing()
    
    #カラムを作成        
    layer.dataProvider().addAttributes( [
        QgsField('ステーションID'            , QVariant.String), 
        QgsField('ステーション名'                  , QVariant.String), 
        QgsField('ステーション名_略称'            , QVariant.String), 
        QgsField('最大駐輪可能台数（ラック数）'              , QVariant.String),
        QgsField('住所'               , QVariant.String), 
        QgsField('道路・交差点名称'          , QVariant.String), 
        QgsField('リージョンID'             , QVariant.String), 
        QgsField('郵便番号'             , QVariant.String), 
        QgsField('決済方法'        , QVariant.String),   
        QgsField('仮想ステーションフラグ'    , QVariant.Bool), 
        #QgsField('仮想ステーション領域'          , QVariant.String), 
        QgsField('駐輪場種別'          , QVariant.String), 
        QgsField('駐輪フープフラグ'          , QVariant.Bool), 
        QgsField('電話番号'        , QVariant.String),  
        #QgsField('vehicle_capacity'      , QVariant.String), 
        QgsField('vehicle_type_capacity' , QVariant.String), 
        QgsField('係員フラグ'      , QVariant.String), 
        QgsField('チャージャーステーションフラグ'   , QVariant.Bool), 
        QgsField('android-uri'               , QVariant.String), 
        QgsField('ios-uri'                  , QVariant.String), 
        QgsField('web-uri'                   , QVariant.String),
        QgsField('lon'                   , QVariant.Double), 
        QgsField('lat'                   , QVariant.Double) 
        ] )
    
    
    #update
    layer.updateFields()
    
    # Addition of features
    for station in gbfs_stations:
        f = QgsFeature()
        f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(station["lon"],station["lat"])))
        
        feature = []
        
        feature.append(station['station_id'           ] if 'station_id'            in station else None)
        feature.append(station['name'                 ] if 'name'                  in station else None)
        feature.append(station['short_name'           ] if 'short_name'            in station else None)
        feature.append(station['capacity'             ] if 'capacity'              in station else None)
        feature.append(station['address'              ] if 'address'               in station else None)
        feature.append(station['cross_street'         ] if 'cross_street'          in station else None)
        feature.append(station['region_id'            ] if 'region_id'             in station else None)
        feature.append(station['post_code'            ] if 'post_code'             in station else None)
        feature.append(", ".join(station['rental_methods']) if 'rental_methods'    in station else None)
        feature.append(station['is_virtual_station'   ] if 'is_virtual_station'    in station else None)
        #feature.append(station['station_area'         ] if 'station_area'          in station else None)
        feature.append(station['parking_type'         ] if 'parking_type'          in station else None)
        feature.append(station['parking_hoop'         ] if 'parking_hoop'          in station else None)
        feature.append(station['contact_phone '       ] if 'contact_phone '        in station else None)
        #feature.append(station['vehicle_capacity'     ] if 'vehicle_capacity'      in station else None)
        feature.append('\n'.join([f"{key}: {value}" for key, value in station['vehicle_type_capacity'].items()]) if 'vehicle_type_capacity' in station else None)
        feature.append(station['is_valet_station'     ] if 'is_valet_station'      in station else None)
        feature.append(station['is_charging_station'  ] if 'is_charging_station'   in station else None)
        feature.append(station['android'              ] if 'android'               in station else None)
        feature.append(station['ios '                 ] if 'ios '                  in station else None)
        feature.append(station['web'                  ] if 'web'                   in station else None)
        feature.append(station['lon'                  ] if 'lon'                   in station else None)
        feature.append(station['lat'                  ] if 'lat'                   in station else None)
        
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
        