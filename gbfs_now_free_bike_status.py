import os, requests, json

from qgis.core import *
from qgis.PyQt.QtCore import QVariant
BIKE_PNG_PATH = os.path.join(os.path.dirname(__file__),  "bike.png")


#ステーション情報を表示
def create_gbfs_free_bike_layer(self,url):
    
    #ステーション情報取得
    response = requests.get(url)
    text = response.text
    data = json.loads(text)
    
    #free_bike情報保持
    gbfs_free_bike = data["data"]["bikes"]
    #self.stations_info = gbfs_free_bike
    
    #create qgisVectorLayer
    layer = QgsVectorLayer("Point", self.system_name + "_free_bike", "memory")
    
    # Start of the edition 
    layer.startEditing()
    
    #カラムを作成        
    layer.dataProvider().addAttributes( [
        QgsField('bike_id'               , QVariant.String), 
        QgsField('is_reserved'           , QVariant.Bool), 
        QgsField('is_disabled'           , QVariant.Bool), 
        QgsField('vehicle_type_id'       , QVariant.String), 
        QgsField('last_reported'         , QVariant.String), 
        QgsField('current_range_meters'  , QVariant.String), 
        QgsField('current_fuel_percent'  , QVariant.String), 
        QgsField('station_id'            , QVariant.String), 
        QgsField('home_station_id'       , QVariant.String), 
        QgsField('pricing_plan_id'       , QVariant.String), 
        QgsField('vehicle_equipment'     , QVariant.String), 
        QgsField('available_until'       , QVariant.String),
        QgsField('android'               , QVariant.String), 
        QgsField('ios '                  , QVariant.String), 
        QgsField('web'                   , QVariant.String),  
        QgsField('lon'                   , QVariant.Double), 
        QgsField('lat'                   , QVariant.Double) 
        ] )
    
    
    #update
    layer.updateFields()
    
    # Addition of features
    for bike in gbfs_free_bike:
        f = QgsFeature()
        f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(bike["lon"],bike["lat"])))
        
        feature = []
        
        feature.append(bike['bike_id'              ] if 'bike_id'              in bike else None)
        feature.append(bike['is_reserved'          ] if 'is_reserved'          in bike else None)
        feature.append(bike['is_disabled'          ] if 'is_disabled'          in bike else None)
        feature.append(bike['vehicle_type_id'      ] if 'vehicle_type_id'      in bike else None)
        feature.append(bike['last_reported'        ] if 'last_reported'        in bike else None)
        feature.append(bike['current_range_meters' ] if 'current_range_meters' in bike else None)
        feature.append(bike['current_fuel_percent' ] if 'current_fuel_percent' in bike else None)
        feature.append(bike['station_id'           ] if 'station_id'           in bike else None)
        feature.append(bike['home_station_id'      ] if 'home_station_id'      in bike else None)
        feature.append(bike['pricing_plan_id'      ] if 'pricing_plan_id'      in bike else None)
        feature.append(bike['vehicle_equipment'    ] if 'vehicle_equipment'    in bike else None)
        feature.append(bike['available_until'      ] if 'available_until'      in bike else None)
        feature.append(bike['android'              ] if 'android'              in bike else None)
        feature.append(bike['ios '                 ] if 'ios '                 in bike else None)
        feature.append(bike['web'                  ] if 'web'                  in bike else None)
        feature.append(bike['lon'                  ] if 'lon'                  in bike else None)
        feature.append(bike['lat'                  ] if 'lat'                  in bike else None)
       
        f.setAttributes(feature)
        layer.addFeature(f)            
    
    # saving changes and adding the layer
    layer.updateExtents() 
    QgsProject.instance().addMapLayer(layer)
    
    #set layer symbol
    symbol = QgsRasterMarkerSymbolLayer(BIKE_PNG_PATH)
    symbol.setSize(5)
    layer.renderer().symbol().changeSymbolLayer(0, symbol )
    
    layer.commitChanges()

#ステーション情報を表示(jp-style)
def create_gbfs_free_bike_layer_jp(self,url):

    
    #ステーション情報取得
    response = requests.get(url)
    text = response.text
    data = json.loads(text)
    
    #free_bike情報保持
    gbfs_free_bike = data["data"]["bikes"]
    #self.stations_info = gbfs_free_bike
    
    #create qgisVectorLayer
    layer = QgsVectorLayer("Point", self.system_name + "_free_bike", "memory")
    
    # Start of the edition 
    layer.startEditing()
    
    #カラムを作成        
    layer.dataProvider().addAttributes( [
        QgsField('車両ID'                     , QVariant.String), 
        QgsField('予約状況（True:予約中）'    , QVariant.Bool), 
        QgsField('車両利用可否(True:利用不可)', QVariant.Bool), 
        QgsField('車種ID'                     , QVariant.String), 
        QgsField('ステータス最終取得時間'     , QVariant.String), 
        QgsField('残走行可能距離(m)'          , QVariant.String), 
        QgsField('残燃料(%)'                  , QVariant.String), 
        QgsField('ステーションID'             , QVariant.String), 
        QgsField('ホームステーションID'       , QVariant.String), 
        QgsField('料金プランID'               , QVariant.String), 
        QgsField('車両装備'                   , QVariant.String), 
        QgsField('車両返却期限'               , QVariant.String),
        QgsField('android'                    , QVariant.String), 
        QgsField('ios '                       , QVariant.String), 
        QgsField('web'                        , QVariant.String),  
        QgsField('lon'                        , QVariant.Double), 
        QgsField('lat'                        , QVariant.Double) 
        ] )
    
    
    #update
    layer.updateFields()
    
    # Addition of features
    for bike in gbfs_free_bike:
        f = QgsFeature()
        f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(bike["lon"],bike["lat"])))
        
        feature = []
        
        feature.append(bike['bike_id'              ] if 'bike_id'              in bike else None)
        feature.append(bike['is_reserved'          ] if 'is_reserved'          in bike else None)
        feature.append(bike['is_disabled'          ] if 'is_disabled'          in bike else None)
        feature.append(bike['vehicle_type_id'      ] if 'vehicle_type_id'      in bike else None)
        feature.append(bike['last_reported'        ] if 'last_reported'        in bike else None)
        feature.append(bike['current_range_meters' ] if 'current_range_meters' in bike else None)
        feature.append(bike['current_fuel_percent' ] if 'current_fuel_percent' in bike else None)
        feature.append(bike['station_id'           ] if 'station_id'           in bike else None)
        feature.append(bike['home_station_id'      ] if 'home_station_id'      in bike else None)
        feature.append(bike['pricing_plan_id'      ] if 'pricing_plan_id'      in bike else None)
        feature.append(bike['vehicle_equipment'    ] if 'vehicle_equipment'    in bike else None)
        feature.append(bike['available_until'      ] if 'available_until'      in bike else None)
        feature.append(bike['android'              ] if 'android'              in bike else None)
        feature.append(bike['ios '                 ] if 'ios '                 in bike else None)
        feature.append(bike['web'                  ] if 'web'                  in bike else None)
        feature.append(bike['lon'                  ] if 'lon'                  in bike else None)
        feature.append(bike['lat'                  ] if 'lat'                  in bike else None)
       
        f.setAttributes(feature)
        layer.addFeature(f)            
    
    # saving changes and adding the layer
    layer.updateExtents() 
    QgsProject.instance().addMapLayer(layer)
    
    #set layer symbol
    symbol = QgsRasterMarkerSymbolLayer(BIKE_PNG_PATH)
    symbol.setSize(5)
    layer.renderer().symbol().changeSymbolLayer(0, symbol )
    
    layer.commitChanges()
        