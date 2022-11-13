# GBFS-NOW


このQGISプラグインはGBFSデータの取得～表示を行うプラグインです。  

GBFS（General Bikeshare Feed Specification）はマイクロモビリティデータの国際標準規格で、多くのシェアモビリティ事業者が本規格でデータを公開しています。  GBFSデータの仕様は下記のGithubで公開されています。  

https://github.com/NABSA/gbfs  

なお日本国内において2022年11月13日時点で対応しているサービスは次の２サービスです。  

---
**- HELLO CYCLING**  
　日本全国のHELLO CYCLINGに加盟するシェアサイクルステーションを公開（**5,607ステーション**）  
　https://www.hellocycling.jp/   
　GBFSメインファイルのURLはhttps://api.odpt.org/api/v4/gbfs/hellocycling/gbfs.json
    
**- docomo Bike Share tokyo**  
　ドコモの運営する東京自転車シェアリングのポートを公開（**1,161ポート**）  
　https://docomo-cycle.jp/tokyo-project/  
　GBFSメインファイルのURLはhttps://api.odpt.org/api/v4/gbfs/docomo-cycle-tokyo/gbfs.json
 
---
 
 
> **Note**
> このQGISプラグインはQGIS3.2およびGBFSver2.3で動作確認をしています。

<img width="600" alt="plugin_image" src="https://user-images.githubusercontent.com/13606213/201525729-d4ba1e0d-beb2-490e-a3ed-b545a4602678.png">


# 事前設定
### 本プラグインを下記ディレクトリに格納するか、QGISの「プラグインの管理とインストール」機能にてGBFS-NOWを検索してください。  

Windows
>C:\Users\user_name\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\gbfs_now

Mac
>/Users/user_name/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/gbfs_now

### プラグインを有効にします。  
<img width="600" alt="plugin_search" src="https://user-images.githubusercontent.com/13606213/169724659-ce130555-2cfb-4285-b0be-c97a07204646.png">


# プラグインの使用方法
GBFSを見るまでに３ステップあります。  
  
## 1.GBFSメインファイル（gbfs.json）のURLを指定  
  
メインファイルのファイル名は"gbfs.json"です。   
直接URLを入力するか、ツールボタンからカタログリストを表示して公開されているGBFSを選択してください。  
カタログリストはこちらのURLから取得しています。  
  
https://github.com/NABSA/gbfs/blob/master/systems.csv  
  

詳細ボタンを選択すると、GBFS公式Githubより各社のGBFSデータのURLが一覧表示されます。どれか一行を選択してウィンドウを閉じると、URLが転記されます。  
<img width="600" alt="gbfs_search" src="https://user-images.githubusercontent.com/13606213/201524951-d7c74dba-168b-47ac-ac0b-52da4134ac1e.png">


## 2.言語選択  
  
指定したGBFSファイルが多言語対応している場合、GBFSメインファイルには各言語のファイルリンクが入っています（多言語対応の状況は事業者に依存します）。  
対応言語の一覧が表示されるので、選択してください。未選択の場合、最初の言語が選択されます。  
  
<img width="600" alt="language_image" src="https://user-images.githubusercontent.com/13606213/201525383-cb9a4124-3a65-43fa-93b0-9032d06b6614.png">
  
## 3.各種表示設定  
  
2条件を設定します。  
・ステーションの現況を表示するか否か（"station_status.json"）  
・表示する際、カラム名（列名）を日本語表記するか否か  
  
 <img width="600" alt="setting_image" src="https://user-images.githubusercontent.com/13606213/201525437-7374f795-cda1-4216-a8a5-ae9754a391a8.png">



# 表示されるもの
  
表示されるもの  
- システム概要　　　：システム名、システム運用事業者名、サービスURL、アプリStorリンクなど  
- ステーション情報　：ステーション名、緯度経度、最大駐輪可能台数（ラック数）など  ※ステーション型サービスの場合
- ステーション現況　：貸出可能台数、駐輪可能台数、営業時間内/外、データ更新時点 　※ステーション型サービスの場合
- フリー車両情報　　：車両現在地、予約状況など　※ドックレス型サービスの場合

<img width="600" alt="plugin_image2" src="https://user-images.githubusercontent.com/13606213/201525624-fddfc9ff-12c8-42eb-9b8d-1dc0082427a7.png">

<img width="600" alt="plugin_image3" src="https://user-images.githubusercontent.com/13606213/201525577-2401867f-2424-4afe-9527-e328ec9d7f0d.png">

# アイコンについて

<img width="30" alt="station" src="https://user-images.githubusercontent.com/13606213/201525775-eefc5694-7062-4e8e-9647-a092e69d5c86.png">ステーションピン（ステーション情報）

<img width="30" alt="station_now" src="https://user-images.githubusercontent.com/13606213/201525759-4419408d-5bad-4580-9b45-e00e05c98eb6.png">ステーションピン（ステーション現況）

<img width="30" alt="bike" src="https://user-images.githubusercontent.com/13606213/201525783-c7243103-8dd3-4e0f-af3e-bdcf6d08e437.png">自転車アイコン（フリー車両の所在地）



さあ、始めましょう！
