# -*- coding: utf-8 -*-
# checks the number of residents in the kml based on the downladed csv
from config import get_config
import xml.etree.ElementTree as et
import pandas as pd
import random
import requests

KML = r"D:\git\tools-drones\temp\residents_km_tiles.kml"
CVS = r"D:\git\tools-drones\temp\volkszaehlung-bevoelkerungsstatistik_einwohner_2021_2056.csv"
NUMBEROFTESTS = 1


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


def towgs84(e, n):
    try:
        cfg = get_config()
        for idx in range(cfg["maxtriesReframe"]):
            params = {"easting": e, "northing": n, "format": "json"}
            response = requests.get(cfg["ReframeLV95ToWGS84"], params=params)
            if response.status_code == 200:
                # Request was successful
                data = response.json()
                return [data["easting"], data["northing"]]
            else:
                print(
                    "Request failed with status code: {} at {} {} try: {}".format(response.status_code, e, n, idx)
                )
    except Exception as e:
        print("Max tries to reframe reached, return coord 0,0. Errormsg = {}".format(e))
        return None


def run():
    kmldict = readkml()
    csvdata = pd.read_csv(CVS, delimiter=";")
    # indexarr = getindexarr(len(csvdata.index) - 1)
    indexarr = getindexarr(len(csvdata.index) - 1)
    for idx in indexarr:
        print(idx)
        row = csvdata.loc[idx]
        lv03idx = str(row["RELI"])
        east = int(lv03idx[:-5]) * 1000 + 2000000
        north = int(lv03idx[4:-1]) * 1000 + 1000000
        print("{} {} {}".format(lv03idx,east,north))
        kmlkey = "{}{}".format(int(east/1000), int(north/1000))
        print(kmldict[kmlkey])
        condition = (csvdata["E_KOORD"] >= east) & (csvdata["E_KOORD"] < east + 1000) & (csvdata["N_KOORD"] >= north) & (csvdata["N_KOORD"] < north + 1000)
        selected_data = csvdata[condition]
        sumresidents = 0
        for index, row in selected_data.iterrows():
            sumresidents += row["NUMMER"]
        if sumresidents == int(kmldict[kmlkey]["description"].split(":")[1]):
            print("OK")
        else:
            print("NOK")
        easting, northing = towgs84(east, north)
        if easting == kmldict[kmlkey]["coordinates"][0].split(",")[0]:
            print("Coord OK")
            print(easting)
            print(northing)
        else:
            print(easting)
            print(float(kmldict[kmlkey]["coordinates"][0].split(",")[0]))
            print(easting - float(kmldict[kmlkey]["coordinates"][0].split(",")[0]))


# https://s.geo.admin.ch/9f8892eddc
# 49071188 LB ist in LV95
# 2'490'000 / 1'118'000
if __name__ == "__main__":
    run()



