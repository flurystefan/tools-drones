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

- tool-residents.py 
  -c ch.bfs.volkszaehlung-bevoelkerungsstatistik_einwohner 
  -o D:\git\tools-drones\temp 
  -f KML KMZ
