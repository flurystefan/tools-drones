# -*- coding: utf-8 -*-
# checks the number of residents in the kml based on the downladed csv
from config import get_config
import xml.etree.ElementTree as et

KML = r"D:\git\tools-drones\temp\residents_km_tiles.kml"
CVS = r"D:\git\tools-drones\temp\volkszaehlung-bevoelkerungsstatistik_einwohner_2021_2056.csv"

def readkml():
    tree = et.parse(KML)
    root = tree.getroot()
    placemarks = root.findall(".//{http://www.opengis.net/kml/2.2}Placemark")
    for placemark in placemarks:
        name = placemark.find('.//{http://www.opengis.net/kml/2.2}name').text
        coordinates = placemark.find('.//{http://www.opengis.net/kml/2.2}coordinates').text
        print(name)
        print(coordinates)


def run(cfg):
    readkml()

if __name__ == "__main__":
    run(get_config())


ET.ElementTree
