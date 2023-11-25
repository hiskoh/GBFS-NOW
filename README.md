README（日本語版）はこちらをご覧ください  
https://github.com/hiskoh/GBFS-NOW/blob/main/README-JP.md

---

# GBFS-NOW

This QGIS plug-in performs everything from acquisition to display of GBFS data.
GBFS (General Bikeshare Feed Specification) is an international standard for micromobility data, and many shared mobility operators publish their data under this standard.The GBFS data specification is available on Github.  
  
https://github.com/NABSA/gbfs  

The following two services are supported in Japan as of November 13, 2022.  

---
**- HELLO CYCLING**  
　Share cycle stations affiliated with HELLO CYCLING are available in Japan（**5,607 Stations**）  
　https://www.hellocycling.jp/   
　GBFS.json-URL https://api.odpt.org/api/v4/gbfs/hellocycling/gbfs.json
    
**- docomo Bike Share tokyo**  
　Tokyo Bike Sharing ports operated by docomo are available to the public（**1,161 Ports**）  
　https://docomo-cycle.jp/tokyo-project/  
　GBFS.json-URL https://api.odpt.org/api/v4/gbfs/docomo-cycle-tokyo/gbfs.json
 
--- 
 
> **Note**
> This QGIS plug-in has been tested with QGIS3.2 and GBFSver2.3.

<img width="600" alt="plugin_image" src="https://user-images.githubusercontent.com/13606213/201525729-d4ba1e0d-beb2-490e-a3ed-b545a4602678.png">



# Setting
Please store this plug-in in the following directory or Search for GBFS-NOW in the "Manage and Install Plugins" function of QGIS.

Windows
>C:\Users\user_name\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\gbfs_now

Mac
>/Users/user_name/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/gbfs_now

### Activate the plugin

<img width="600" alt="plugin_search" src="https://user-images.githubusercontent.com/13606213/169724659-ce130555-2cfb-4285-b0be-c97a07204646.png">


# how to use
There are three steps to viewing the GBFS.  
  
## 1.Enter the GBFS main file URL
  
The file name of the main file is "gbfs.json". 
Enter the URL directly or click the Tools button to display the catalog list and select a publicly available GBFS.
The catalog list is obtained from this URL.  

https://github.com/NABSA/gbfs/blob/master/systems.csv  
  
Selecting the Details button will list the URLs of each company's GBFS data from the official GBFS Github. Select one of the lines and close the window to transcribe the URL.

<img width="600" alt="gbfs_search" src="https://user-images.githubusercontent.com/13606213/201524951-d7c74dba-168b-47ac-ac0b-52da4134ac1e.png">


## 2.Select a language.  
    
GBFS main file contains file links for each language. ※Multilingual support is dependent on the operator.  
A list of supported languages will be displayed. Please select one. If not selected, the first language will be selected.   

<img width="600" alt="language_image" src="https://user-images.githubusercontent.com/13606213/201525383-cb9a4124-3a65-43fa-93b0-9032d06b6614.png">
  
## 3.Select display conditions.
  
Select the following two conditions.  
・Whether the current status of the station is displayed or not.  
・Whether column names are displayed in Japanese or not.  
  
 <img width="600" alt="setting_image" src="https://user-images.githubusercontent.com/13606213/201525437-7374f795-cda1-4216-a8a5-ae9754a391a8.png">


# Displayed.
  
What will be displayed  
- System overview: System name, system operator name, service URL, App Stor link, etc.  
- Station information: Station name, latitude and longitude, maximum number of bikes (racks), etc.  *For station service
- Station status: number of available rental units, number of available parked bicycles, during/outside business hours, and time of data update *For station service
- Free bike status: bike current location, reservation status, etc. *For dockless service
  

<img width="600" alt="plugin_image2" src="https://user-images.githubusercontent.com/13606213/201525624-fddfc9ff-12c8-42eb-9b8d-1dc0082427a7.png">

<img width="600" alt="plugin_image3" src="https://user-images.githubusercontent.com/13606213/201525577-2401867f-2424-4afe-9527-e328ec9d7f0d.png">

# Icons

<img width="30" alt="station" src="https://user-images.githubusercontent.com/13606213/201525775-eefc5694-7062-4e8e-9647-a092e69d5c86.png"> station_information

<img width="30" alt="station_now" src="https://user-images.githubusercontent.com/13606213/201525759-4419408d-5bad-4580-9b45-e00e05c98eb6.png"> station_status

<img width="30" alt="bike" src="https://user-images.githubusercontent.com/13606213/201525783-c7243103-8dd3-4e0f-af3e-bdcf6d08e437.png"> free_bike


Let's get started.
