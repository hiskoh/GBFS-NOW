README（日本語版）はこちらをご覧ください  
https://github.com/hiskoh/GBFS-NOW/blob/main/README-JP.md

---

# GBFS-NOW

This QGIS plug-in performs everything from acquisition to display of GBFS data.
GBFS (General Bikeshare Feed Specification) is an international standard for micromobility data, and many shared mobility operators publish their data under this standard.The GBFS data specification is available on Github.  
  
https://github.com/NABSA/gbfs  

The following two services are supported in Japan as of June 28, 2022.  

---
**- HELLO CYCLING**  
　Share cycle stations affiliated with HELLO CYCLING are available in Japan（**5,009 Stations**）  
　https://www.hellocycling.jp/   
　GBFS.json-URL https://api.odpt.org/api/v4/gbfs/hellocycling/gbfs.json
    
**- docomo Bike Share tokyo**  
　Tokyo Bike Sharing ports operated by docomo are available to the public（**1,077 Ports**）  
　https://docomo-cycle.jp/tokyo-project/  
　GBFS.json-URL https://api.odpt.org/api/v4/gbfs/docomo-cycle-tokyo/gbfs.json
 
--- 
 
> **Note**
> This Plugin for QGIS 3.22 and GBFSver2.3.The published data of the ODPT (https://www.odpt.org/) is not strictly GBFS compliant.
This data requires an Access token, so the plug-in is also compliant with the same specification.

> **Note**
> This QGIS plug-in is intended for visualization of GBFS data (station locations) for station-based shared mobility services. It does not implement visualization for dockless services.


![image](https://user-images.githubusercontent.com/13606213/176122064-8df71c49-d10f-4c1a-9bd4-653dac7f7f2e.png)



# Setting
Please store this plug-in in the following directory.

Windows
>C:\Users\user_name\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\gbfs_now

Mac
>/Users/user_name/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/gbfs_now

### Activate the plugin
![image](https://user-images.githubusercontent.com/13606213/169724659-ce130555-2cfb-4285-b0be-c97a07204646.png)


# how to use
There are three steps to viewing the GBFS.  
  
## 1.Enter the GBFS main file URL
  
The file name of the main file is "gbfs.json". 
Enter the URL directly or click the Tools button to display the catalog list and select a publicly available GBFS.
The catalog list is obtained from this URL.  

https://github.com/NABSA/gbfs/blob/master/systems.csv  
  
> **Note**
> The data published on the Japanese ODPT (https://www.odpt.org/) does not strictly conform to the GBFS specification and requires a unique Access token. Please enter the access token following the URL of the main file. Access tokens can be obtained by registering as a developer with ODPT.

  
![image](https://user-images.githubusercontent.com/13606213/176124772-030c3a76-90fb-427a-ab91-bd4c7701afdd.png)

## 2.Select a language.  
    
GBFS main file contains file links for each language. ※Multilingual support is dependent on the operator.  
A list of supported languages will be displayed. Please select one. If not selected, the first language will be selected.   

![image](https://user-images.githubusercontent.com/13606213/176124387-3503ad6e-a647-409a-9c3c-a89d4a628f0f.png)
  
## 3.Select display conditions.
  
Select the following two conditions.  
・Whether the current status of the station is displayed or not.  
・Whether column names are displayed in Japanese or not.  
  
  ![image](https://user-images.githubusercontent.com/13606213/176125157-84de68b0-b93c-4c84-b12b-985754435995.png)


# Displayed.
  
What will be displayed  
- System overview: System name, system operator name, service URL, App Stor link, etc.  
- Station information: Station name, latitude and longitude, maximum number of bikes (racks), etc.  
- Station status: number of available rental units, number of available parked bicycles, during/outside business hours, and time of data update  
  
![image](https://user-images.githubusercontent.com/13606213/176126371-1f34ce41-d145-4223-9249-95b850316080.png)

![image](https://user-images.githubusercontent.com/13606213/176125981-68504f01-3ca0-4319-baec-4b56d75582a2.png)

Let's get started.
