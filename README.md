# tools-drones

Geo-Tools for compliance of drones operation

## install

- install Miniconda  
- conda create --prefix d:\git\tools-drones\python python=3.10.10  
- conda activate d:\git\tools-drones\python  
- conda install -c conda-forge pystac  
- pip install pystac-client  
- pip install simplekml  
- pip install pandas  
- pip install openpyxl (Excel export)  
- pip install geopandas (Buffer)  

## share kml and use it in map.geo.admin.ch

- put kml on google-drive  
- share the kml with anyone with the link  
- take the part after/d/ to the next / (should be the id)  
  for example: 1_jkG6zlbKGRg1W4IaVd41JT3qJQjGCtI  
  <https://drive.google.com/file/d/1_jkG6zlbKGRg1W4IaVd41JT3qJQjGCtI/view?usp=sharing>
- the new url should look like  
  <https://drive.google.com/uc?export=download&id=> plus the id  
  <https://drive.google.com/uc?export=download&id=1_jkG6zlbKGRg1W4IaVd41JT3qJQjGCtI>
  This url can be imported on map.geo.admin.ch in Advanced tools and Import.  
  Copy the url into the field and connect  
- go to Share and you can use the Share link  
  or open Embed and you can use the sniped for a iFrame  

## tools

tool-residents.py  
more details to the parameter you will find in the methode parse_args()  
layer in map.geo.admin.ch  
   -c ch.bfs.volkszaehlung-bevoelkerungsstatistik_einwohner  
output folder  
   -o D:\git\tools-drones\temp  
output format  
   -f KML KMZ  

tool-buffer.py  
more details to the parameter you will find in the methode parse_args()  
KML, local path or link to map.geo.admin.ch with draw  
   -p D:\git\tools-drones\temp\map.geo.admin.ch.kml  
input format  
   -if KML  
[epsg code]"https://epsg.io/"  
   -iepsg 4326  
output format  
   -f KML  
drone wind speed  
   -v0 5.0  
characteristic dimension  
   -cd 0.90  
height flight geography  
   -hfg 45.0  
output folder  
   -o D:\git\tools-drones\temp  

## environments

There are several environments in which the tools or the functionalities are implied.
There are also corresponding .yaml files available for the environments,  
or they run with the installed  
Python standard environments for QGIS and ArcGIS Pro.  

### commandline

cmd_environment.yml  
-tool-residents  
-tool-buffer  

### QGIS

not yet available  

### ArcGIS Pro

not yet available  

### NoGIS but GUI

not yet available  
