# GBFS-NOW


このQGISプラグインはGBFSデータの取得～表示を行うプラグインです。  

GBFS（General Bikeshare Feed Specification）はマイクロモビリティデータの国際標準規格で、多くのシェアモビリティ事業者が本規格でデータを公開しています。  GBFSデータの仕様は下記のGithubで公開されています。  

https://github.com/NABSA/gbfs  

なお日本国内において2022年11月06日時点で対応しているサービスは次の２サービスです。  

---
**- HELLO CYCLING**  
　日本全国のHELLO CYCLINGに加盟するシェアサイクルステーションを公開（**5,569ステーション**）  
　https://www.hellocycling.jp/   
　GBFSメインファイルのURLはhttps://api.odpt.org/api/v4/gbfs/hellocycling/gbfs.json
    
**- docomo Bike Share tokyo**  
　ドコモの運営する東京自転車シェアリングのポートを公開（**1,162ポート**）  
　https://docomo-cycle.jp/tokyo-project/  
　GBFSメインファイルのURLはhttps://api.odpt.org/api/v4/gbfs/docomo-cycle-tokyo/gbfs.json
 
---
 
 
> **Note**
> このQGISプラグインはQGIS3.2およびGBFSver2.3で動作確認をしています。

> **Note**
> このQGISプラグインはステーション型シェアモビリティサービスのGBFSデータ（ステーション所在地）の可視化を想定しています。ドックレス型サービスの可視化は実装していませんのでご注意ください。  

![image](https://user-images.githubusercontent.com/13606213/176122064-8df71c49-d10f-4c1a-9bd4-653dac7f7f2e.png)


# 事前設定
### 本プラグインを下記ディレクトリに格納してください。  

Windows
>C:\Users\user_name\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\gbfs_now

Mac
>/Users/user_name/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/gbfs_now

### プラグインを有効にします。  
![image](https://user-images.githubusercontent.com/13606213/169724659-ce130555-2cfb-4285-b0be-c97a07204646.png)


# プラグインの使用方法
GBFSを見るまでに３ステップあります。  
  
## 1.GBFSメインファイル（gbfs.json）のURLを指定  
  
メインファイルのファイル名は"gbfs.json"です。   
直接URLを入力するか、ツールボタンからカタログリストを表示して公開されているGBFSを選択してください。  
カタログリストはこちらのURLから取得しています。  
  
https://github.com/NABSA/gbfs/blob/master/systems.csv  
  

詳細ボタンを選択すると、GBFS公式Githubより各社のGBFSデータのURLが一覧表示されます。どれか一行を選択してウィンドウを閉じると、URLが転記されます。  
![image](https://user-images.githubusercontent.com/13606213/176148240-3471a297-070f-4896-ac2f-b4c4ac406380.png)


## 2.言語選択  
  
指定したGBFSファイルが多言語対応している場合、GBFSメインファイルには各言語のファイルリンクが入っています（多言語対応の状況は事業者に依存します）。  
対応言語の一覧が表示されるので、選択してください。未選択の場合、最初の言語が選択されます。  
  
![image](https://user-images.githubusercontent.com/13606213/176124387-3503ad6e-a647-409a-9c3c-a89d4a628f0f.png)
  
## 3.各種表示設定  
  
2条件を設定します。  
・ステーションの現況を表示するか否か（"station_status.json"）  
・表示する際、カラム名（列名）を日本語表記するか否か  
  
  ![image](https://user-images.githubusercontent.com/13606213/176125157-84de68b0-b93c-4c84-b12b-985754435995.png)


# 表示されるもの
  
表示されるもの  
- システム概要　　　：システム名、システム運用事業者名、サービスURL、アプリStorリンクなど  
- ステーション情報　：ステーション名、緯度経度、最大駐輪可能台数（ラック数）など  
- ステーション現況　：貸出可能台数、駐輪可能台数、営業時間内/外、データ更新時点

![image](https://user-images.githubusercontent.com/13606213/176126371-1f34ce41-d145-4223-9249-95b850316080.png)

![image](https://user-images.githubusercontent.com/13606213/176125981-68504f01-3ca0-4319-baec-4b56d75582a2.png)

さあ、始めましょう！
