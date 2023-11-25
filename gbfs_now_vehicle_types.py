import requests, json, os
from qgis.core import *
from qgis.PyQt.QtCore import QVariant, Qt, QAbstractTableModel, QUrl
from qgis.PyQt.QtGui import QIcon, QPixmap

from qgis.PyQt.QtNetwork import QNetworkAccessManager, QNetworkRequest,QNetworkReply

NO_IMAGE = os.path.join(os.path.dirname(__file__),  "no_image.png")

def create_gbfs_vehicle_types_viewer(self,url):
 
    #データの取得
    response = requests.get(url)
    text= response.text
    data = json.loads(text)
    
    #vehicle_types情報保持
    vehicle_types = data["data"]["vehicle_types"]

    # モデルの設定
    model = TransposedJsonTableModel(vehicle_types)
    self.vehicle_types_table.setModel(model)
   
    # 画像アイコン行を拡張
    if any(model.icon_urls):
        self.vehicle_types_table.setRowHeight(model.rowCount() - 1, 100)
        
    # 画像アイコン行を拡張
    if any(model.vehicle_image):
        vehicle_image_row_index = len(model.headers) + (1 if any(model.icon_urls) else 0)  # vehicle_imagesの行インデックス
        self.vehicle_types_table.setRowHeight(vehicle_image_row_index, 100)

def clear_gbfs_vehicle_types_viewer(self):
    # モデルのデータをクリアする
    model = self.vehicle_types_table.model()
    if isinstance(model, TransposedJsonTableModel):
        model.clearData()

class TransposedJsonTableModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        
        # QNetworkAccessManager インスタンスの初期化
        self.manager = QNetworkAccessManager()
        self.manager.finished.connect(self.onDownloadFinished)
        
        #その他の初期化
        self.headers = []
        self.data_list = []
        self.icon_urls = []
        self.rows = []
        self.vehicle_image = []
        self.image_cache = {} 
        
        if data:
        
            # icon_urlのリストを抽出
            self.icon_urls = [item['vehicle_assets']['icon_url'] for item in data if 'vehicle_assets' in item]
            
            # vehicle_imageのリストを抽出
            self.vehicle_image = [item['vehicle_image'] for item in data if 'vehicle_image' in item]
            
            # すべての画像をダウンロードしてキャッシュに保存する
            for image_url in self.icon_urls + self.vehicle_image:
            
                request = QNetworkRequest(QUrl(image_url))
                # リダイレクトを許可するフラグを設定
                request.setAttribute(QNetworkRequest.FollowRedirectsAttribute, True)
                #request.setUrl(image_url)
                
                self.manager.get(request)
            
            # キー（列ヘッダー）を取得し、転置データを生成
            # 更新されたデータのキーを取得(vehicle_imageは画像として別で読み込むため除外)
            self.headers = [key for key in data[0].keys() if key != 'vehicle_image']
            # 更新されたデータリストを生成
            self.data_list = [[item[key] for key in self.headers] for item in data]
            # 列ヘッダーを除いた値のみのリスト
            self.rows = list(map(list, zip(*self.data_list)))

    def rowCount(self, parent=None):
        # アイコンURLとvehicle_imageがあるかどうかをチェック
        extra_rows = 0
        if any(self.icon_urls):
            extra_rows += 1
        if any(self.vehicle_image):
            extra_rows += 1
        
        return len(self.headers) + extra_rows

    def columnCount(self, parent=None):
        # 列の数は元のデータの行の数
        return len(self.data_list)

    def data(self, index, role):
        # 通常のテキストデータ
        if role == Qt.DisplayRole:
            # index.row() が self.rows の範囲内にあるかを確認
            if 0 <= index.row() < len(self.rows):
                # index.column() が self.rows[index.row()] の範囲内にあるかを確認
                if 0 <= index.column() < len(self.rows[index.row()]):
                    return self.rows[index.row()][index.column()]
            
        if role == Qt.DecorationRole:
            # アイコンの行またはvehicle_imageの行を処理
            image_url = None
            if self.icon_urls and index.row() == len(self.headers):
                image_url = self.icon_urls[index.column()]
            elif self.vehicle_image and index.row() == len(self.headers) + (1 if any(self.icon_urls) else 0):
                image_url = self.vehicle_image[index.column()]

            if image_url:
                #キャッシュがある場合、キャッシュを返す
                if image_url in self.image_cache:
                    return self.image_cache[image_url]
                #キャッシュがない場合、空欄
                else:
                    return None
                
        return None


    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if section < len(self.data_list):
                    return f"vehicle {section + 1}"
            else:
                if section < len(self.headers):
                    return self.headers[section]
                # アイコン行のヘッダー
                elif self.icon_urls and section == len(self.headers):
                    return "Icon"
                # vehicle_image行のヘッダー
                elif self.vehicle_image and section == len(self.headers) + (1 if any(self.icon_urls) else 0):
                    return "Vehicle Image"
        return None

    def clearData(self):
        # モデルのデータをクリアする
        self.beginResetModel()  # モデルリセットの開始を通知
        # データ構造のクリア
        self.headers.clear()
        self.data_list.clear()
        self.icon_urls.clear()
        self.rows.clear()
        self.endResetModel()  # モデルリセットの終了を通知
        
        

    # ダウンロード完了時の処理
    def onDownloadFinished(self, reply):
        #リクエスト中のURLを取得
        url = reply.request().url().toString()
        if reply.error() == QNetworkReply.NoError:
            data = reply.readAll()
            pixmap = QPixmap()
            pixmap.loadFromData(data)
            scaled_pixmap = pixmap.scaled(150, 150, Qt.KeepAspectRatio)
            icon = QIcon(scaled_pixmap)
            self.image_cache[url] = icon
        else:
            self.image_cache[url] = QIcon(NO_IMAGE)

        # ビューの更新をトリガーする
        # モデルの全データ範囲をカバーするインデックスを作成
        topLeft = self.createIndex(0, 0)
        bottomRight = self.createIndex(self.rowCount() - 1, self.columnCount() - 1)

        # ビューの更新をトリガーするためにdataChanged シグナルを発行
        self.dataChanged.emit(topLeft, bottomRight, [Qt.DecorationRole])
        
        reply.deleteLater()
        
        
       