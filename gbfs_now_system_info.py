import requests, json

from qgis.core import *
from qgis.PyQt.QtCore import QVariant,Qt,QUrl
from qgis.PyQt.QtGui import QPixmap
from qgis.PyQt.QtNetwork import QNetworkAccessManager, QNetworkRequest,QNetworkReply

def create_gbfs_system_info_viewer(self,url):
 
    #データの取得
    response = requests.get(url)
    text= response.text
    data = json.loads(text)
    
    
    #データの整理
    item = data["data"]
    self.system_name = item["name"]
    
    
    system_id                = item["system_id"]            if "system_id"            in item else ''
    language                 = item["language"]             if "language"             in item else ''
    name                     = item["name"]                 if "name"                 in item else ''
    short_name               = item["short_name"]           if "short_name"           in item else ''
    operator                 = item["operator"]             if "operator"             in item else ''
    url                      = item["url"]                  if "url"                  in item else ''
    purchase_url             = item["purchase_url"]         if "purchase_url"         in item else ''
    start_date               = item["start_date"]           if "start_date"           in item else ''
    phone_number             = item["phone_number"]         if "phone_number"         in item else ''
    email                    = item["email"]                if "email"                in item else ''
    feed_contact_email       = item["feed_contact_email"]   if "feed_contact_email"   in item else ''
    timezone                 = item["timezone"]             if "timezone"             in item else ''
    license_url              = item["license_url"]          if "license_url"          in item else ''
    terms_url                = item["terms_url"]            if "terms_url"            in item else ''
    terms_last_updated       = item["terms_last_updated"]   if "terms_last_updated"   in item else ''
    privacy_url              = item["privacy_url"]          if "privacy_url"          in item else ''
    privacy_last_updated     = item["privacy_last_updated"] if "privacy_last_updated" in item else ''
    
        
    if "brand_assets" in item:
        brand_last_modified  = item["brand_assets"]["brand_last_modified" ] if "brand_last_modified"  in item["brand_assets"] else ''
        brand_terms_url      = item["brand_assets"]["brand_terms_url"     ] if "brand_terms_url"      in item["brand_assets"] else ''
        brand_image_url      = item["brand_assets"]["brand_image_url"     ] if "brand_image_url"      in item["brand_assets"] else ''
        brand_image_url_dark = item["brand_assets"]["brand_image_url_dark"] if "brand_image_url_dark" in item["brand_assets"] else ''
        color                = item["brand_assets"]["color"               ] if "color"                in item["brand_assets"] else ''
    else:
        brand_last_modified  = ''
        brand_terms_url      = ''
        brand_image_url      = ''
        brand_image_url_dark = ''
        color                = ''
        
    android_store_uri = ''
    ios_store_uri     = ''
    
    if "rental_apps" in item:
        android_store_uri = item["rental_apps"]["android"]["store_uri"] if "android" in item["rental_apps"] and "store_uri" else ''
        ios_store_uri = item["rental_apps"]["ios"]["store_uri"] if "ios" in item["rental_apps"] and "store_uri" else ''
    
    #ブランド画像のダウンロード＆表示
    download_image(self,self.brand_image,brand_image_url)

    #ラベル表示
    self.label_name.setText(name)
#    self.label_short_name.setText(short_name)
    self.label_language.setText(language)
    self.label_operator.setText(operator)
    self.label_start_date.setText(start_date)
 
    self.label_url.setText("<a href=\""+ url + "\">" + url +"</a>") 
    self.label_license_url.setText("<a href=\""+ license_url + "\">" + license_url +"</a>") 
    self.label_brand_terms_url.setText("<a href=\""+ brand_terms_url + "\">" + brand_terms_url +"</a>")
    self.label_terms_url.setText("<a href=\""+ terms_url + "\">" + terms_url +"</a>")
    self.label_privacy_url.setText("<a href=\""+ privacy_url +"\">" + privacy_url +"</a>")
    self.label_android.setText("<a href=\""+ android_store_uri +"\">" + android_store_uri +"</a>")
    self.label_ios.setText("<a href=\""+ ios_store_uri +"\">" + ios_store_uri +"</a>")

def download_image(self, target_label, url):
    self.manager = QNetworkAccessManager()
    self.manager.finished.connect(lambda reply: set_image(self, reply, target_label))
    self.manager.get(QNetworkRequest(QUrl(url)))

def set_image(self, reply, target_label):
    if reply.error() == QNetworkReply.NoError:
        data = reply.readAll()
        pixmap = QPixmap()
        pixmap.loadFromData(data)
        scaled_pixmap = pixmap.scaled(150, 150, Qt.KeepAspectRatio)  # サイズ変更
        target_label.setPixmap(scaled_pixmap)
    else:
        target_label.clear()
    
    
def clear_gbfs_system_info_viewer(self):
    self.label_name.clear()
    self.label_language.clear()
    self.label_operator.clear()
    self.label_start_date.clear()
    self.label_url.clear()
    self.label_license_url.clear()
    self.label_brand_terms_url.clear()
    self.label_terms_url.clear()
    self.label_privacy_url.clear()
    self.label_android.clear()
    self.label_ios.clear()