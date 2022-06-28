# GBFS-NOW


このQGISプラグインはGBFSデータの取得から表示までを行います。  

GBFS（General Bikeshare Feed Specification）はマイクロモビリティデータの国際標準規格で、多くのシェアモビリティ事業者が本規格でデータを公開しています。  GBFSデータの仕様は下記のGithubで公開されています。  

This QGIS plug-in performs everything from acquisition to display of GBFS data.
GBFS (General Bikeshare Feed Specification) is an international standard for micromobility data, and many shared mobility operators publish their data under this standard.The GBFS data specification is available on Github.  
  
https://github.com/NABSA/gbfs  

なお日本国内において2022年6月28日時点で対応しているサービスは次の２サービスです。

**HELLO CYCLING**  
　日本全国のHELLO CYCLINGに加盟するシェアサイクルステーションを公開（5,009ステーション）  
　https://www.hellocycling.jp/   
    
**ドコモ・バイクシェア(東京)**  
　ドコモの運営する東京自転車シェアリングのポートを公開（1,077ポート）  
　https://docomo-cycle.jp/tokyo-project/  
   
The following two services are supported in Japan as of June 28, 2022.

HELLO CYCLING  
　Share cycle stations affiliated with HELLO CYCLING are available in Japan (5,009 stations).  
  https://www.hellocycling.jp/   
    
docomo Bike Share  
　Tokyo Bike Sharing ports operated by docomo are available to the public (1,077 ports).  
　https://docomo-cycle.jp/tokyo-project/  
 
> **Note**
> このQGISプラグインはQGIS3.2およびGBFSver2.3で動作確認をしています。また、日本のODPT（https://www.odpt.org/ ）で公開でされるデータは厳密にはGBFS仕様に準拠しておらず、独自のAccessトークンが必要となっています。本プラグインは同仕様もサポートしています。  
> This Plugin for QGIS 3.22 and GBFSver2.3.The published data of the ODPT (https://www.odpt.org/) is not strictly GBFS compliant.
This data requires an Access token, so the plug-in is also compliant with the same specification.

> **Note**
> このQGISプラグインはステーション型シェアモビリティサービスのGBFSデータ（ステーション所在地）の可視化を想定しています。ドックレス型サービスの可視化は実装していませんのでご注意ください。  
> This QGIS plug-in is intended for visualization of GBFS data (station locations) for station-based shared mobility services. It does not implement visualization for dockless services.


![image](https://user-images.githubusercontent.com/13606213/176122064-8df71c49-d10f-4c1a-9bd4-653dac7f7f2e.png)



# Setting
### 本プラグインを下記ディレクトリに格納してください。  
Please store this plug-in in the following directory.

Windows
>C:\Users\user_name\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\gbfs_now

Mac
>/Users/user_name/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/gbfs_now

### プラグインを有効にします。  
Activate the plugin
![image](https://user-images.githubusercontent.com/13606213/169724659-ce130555-2cfb-4285-b0be-c97a07204646.png)


# how to use
GBFSを見るまでに３ステップあります。  
There are three steps to viewing the GBFS.  
  
## 1.Enter the GBFS main file URL
  
メインファイルのファイル名は"gbfs.json"です。   
直接URLを入力するか、ツールボタンからカタログリストを表示して公開されているGBFSを選択してください。  
カタログリストはこちらのURLから取得しています。  
  
The file name of the main file is "gbfs.json". 
Enter the URL directly or click the Tools button to display the catalog list and select a publicly available GBFS.
The catalog list is obtained from this URL.  

https://github.com/NABSA/gbfs/blob/master/systems.csv  
  
> **Note**
> 日本のODPT（https://www.odpt.org/ ）で公開でされるデータは厳密にはGBFS仕様に準拠しておらず、独自のAccessトークンが必要となっています。メインファイルのURLに続きアクセストークンを入力してください。アクセストークンはODPTに開発者登録することで取得できます。  
> The data published on the Japanese ODPT (https://www.odpt.org/) does not strictly conform to the GBFS specification and requires a unique Access token. Please enter the access token following the URL of the main file. Access tokens can be obtained by registering as a developer with ODPT.

  
![image](https://user-images.githubusercontent.com/13606213/176124772-030c3a76-90fb-427a-ab91-bd4c7701afdd.png)

## 2.Select a language.  
  
GBFSメインファイルには各言語のファイルリンクが入っています。  
※多言語対応の状況は事業者に依存します。  
対応言語の一覧が表示されるので、選択してください。  
未選択の場合、最初の言語が選択されます。  
  
GBFS main file contains file links for each language. ※Multilingual support is dependent on the operator.  
A list of supported languages will be displayed. Please select one. If not selected, the first language will be selected.   


![image](https://user-images.githubusercontent.com/13606213/176124387-3503ad6e-a647-409a-9c3c-a89d4a628f0f.png)
  
## 3.Select display conditions.
  
2条件を設定します。  
・ステーションの現況を表示するか否か（"station_status.json"）  
・表示する際、カラム名（列名）を日本語表記するか否か  
  
Select the following two conditions.  
・Whether the current status of the station is displayed or not.  
・Whether column names are displayed in Japanese or not.  
  
  ![image](https://user-images.githubusercontent.com/13606213/176125157-84de68b0-b93c-4c84-b12b-985754435995.png)


# Displayed.
  
表示されるもの  
- システム概要　　　：システム名、システム運用事業者名、サービスURL、アプリStorリンクなど  
- ステーション情報　：ステーション名、緯度経度、最大駐輪可能台数（ラック数）など  
- ステーション現況　：貸出可能台数、駐輪可能台数、営業時間内/外、データ更新時点

What will be displayed  
- System overview: System name, system operator name, service URL, App Stor link, etc.  
- Station information: Station name, latitude and longitude, maximum number of bikes (racks), etc.  
- Station status: number of available rental units, number of available parked bicycles, during/outside business hours, and time of data update  
  
![image](https://user-images.githubusercontent.com/13606213/176126371-1f34ce41-d145-4223-9249-95b850316080.png)

![image](https://user-images.githubusercontent.com/13606213/176125981-68504f01-3ca0-4319-baec-4b56d75582a2.png)
