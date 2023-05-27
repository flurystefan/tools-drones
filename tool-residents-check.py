# -*- coding: utf-8 -*-
# checks the number of residents in the kml based on the downladed csv
from config import get_config
import xml.etree.ElementTree as et
import pandas as pd
import random

KML = r"D:\git\tools-drones\temp\residents_km_tiles.kml"
CVS = r"D:\git\tools-drones\temp\volkszaehlung-bevoelkerungsstatistik_einwohner_2021_2056.csv"
NUMBEROFTESTS = 2


def readkml():
    kmldict = {}
    tree = et.parse(KML)
    root = tree.getroot()
    placemarks = root.findall(".//{http://www.opengis.net/kml/2.2}Placemark")
    for placemark in placemarks:
        name = placemark.find('.//{http://www.opengis.net/kml/2.2}name').text
        coordinates = placemark.find('.//{http://www.opengis.net/kml/2.2}coordinates').text
        description = placemark.find('.//{http://www.opengis.net/kml/2.2}description').text
        kmldict[name] = {"description": description, "coordinates": coordinates.split(" ")}
    return kmldict


def getindexarr(maxidx):
    idxs = []
    for i in range(NUMBEROFTESTS):
        idxs.append(random.randint(0, maxidx))
    return idxs


def run(cfg):
    kmldict = readkml()
    csvdata = pd.read_csv(CVS, delimiter=";")
    indexarr = getindexarr(len(csvdata.index) - 1)
    for idx in indexarr:
        print(idx)
        row = csvdata.loc[0]
        condition = csvdata["RELI"] == 49071188
        row1 = csvdata[condition]
        print(csvdata.columns)



# https://s.geo.admin.ch/9f8892eddc
# 49071188 LB ist in LV95
# 2'490'000 / 1'118'000
if __name__ == "__main__":
    run(get_config())

