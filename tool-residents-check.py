# -*- coding: utf-8 -*-
# checks the number of residents in the kml based on the downladed csv in two ways
# NUMBEROFTESTS is the number of random km's
# DEFAREASARR are defined areas in LV95 km's
# use this https://s.geo.admin.ch/9f8892eddc
from config import get_config
import xml.etree.ElementTree as et
import pandas as pd
import random
import requests

KML = r"D:\git\tools-drones\temp\residents_km_tiles.kml"
CVS = r"D:\git\tools-drones\temp\volkszaehlung-bevoelkerungsstatistik_einwohner_2021_2056.csv"
EDGEIDX = {"LB": 0, "LT": 3, "RT": 2, "RB": 1}
NUMBEROFTESTS = 30
DEFAREASARR = ["2488-1111", "2493-1117", "2724-1076"]


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
    print("Found {} polygons in the kml".format(len(kmldict)))
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


def check_residents(east_lv95, north_lv95, csvdata, kmldata, kmlkey, verbose=False):
    condition = (csvdata["E_KOORD"] >= east_lv95) \
                & (csvdata["E_KOORD"] < east_lv95 + 1000) \
                & (csvdata["N_KOORD"] >= north_lv95) \
                & (csvdata["N_KOORD"] < north_lv95 + 1000)
    selected_data = csvdata[condition]
    sumresidents = 0
    for index, row in selected_data.iterrows():
        sumresidents += row["NUMMER"]
    if sumresidents == int(kmldata[kmlkey]["description"].split(":")[1]):
        if verbose:
            print("Number of residents {} at E {} N {}". format(sumresidents, east_lv95, north_lv95))
        return True
    else:
        print("!!! Error !!! Sumresidents failed for E {} N {} KMLValue: {} SumInCsv: {}".format(
            east_lv95, north_lv95, kmldata[kmlkey]["description"].split(":")[1], sumresidents)
        )
        return False


def check_coords(easting, northing, kmldata, kmlkey, idx):
    kml_koords = kmldata[kmlkey]["coordinates"][idx].split(",")
    if easting == kml_koords[0] and northing == kml_koords[1]:
        return True
    else:
        print("!!! Error !!! Coords are not identical KML {} {} CSV {} {}".format(
            kml_koords[0], kml_koords[1], easting, northing)
        )
        return False


def check(east_lv95, north_lv95, csvdata, kmldata, verbose=False):
    kmok = True
    kmlkey = "{}{}".format(int(east_lv95 / 1000), int(north_lv95 / 1000))
    if not check_residents(east_lv95, north_lv95, csvdata, kmldata, kmlkey, verbose):
        kmok = False
    easting, northing = towgs84(east_lv95, north_lv95)
    if not check_coords(easting, northing, kmldata, kmlkey, EDGEIDX["LB"]):
        kmok = False
    easting, northing = towgs84(east_lv95, north_lv95 + 1000)
    if not check_coords(easting, northing, kmldata, kmlkey, EDGEIDX["LT"]):
        kmok = False
    easting, northing = towgs84(east_lv95 + 1000, north_lv95 + 1000)
    if not check_coords(easting, northing, kmldata, kmlkey, EDGEIDX["RT"]):
        kmok = False
    easting, northing = towgs84(east_lv95 + 1000, north_lv95)
    if not check_coords(easting, northing, kmldata, kmlkey, EDGEIDX["RB"]):
        kmok = False
    if kmok:
        return True
    else:
        print("!!! ERROR !!! Error found for km E {} N {}".format(east_lv95, north_lv95))
        return False


def run():
    kmldict = readkml()
    csvdata = pd.read_csv(CVS, delimiter=";")
    print("Found {} lines in the csv".format(len(csvdata.index) - 1))
    indexarr = getindexarr(len(csvdata.index) - 1)
    errcounter = 0
    # check random
    print("--------------------------------------------")
    print("Check random")
    for idx in indexarr:
        lv03idx = str(csvdata.loc[idx]["RELI"])
        east_lv95 = int(lv03idx[:-5]) * 1000 + 2000000
        north_lv95 = int(lv03idx[4:-1]) * 1000 + 1000000
        if check(east_lv95, north_lv95, csvdata, kmldict):
            print("Coord LV95 E {} N {} is OK".format(east_lv95, north_lv95))
        else:
            print("--------------------------------------------")
            print("Coord LV95 E {} N {} is Not OK".format(east_lv95, north_lv95))
            print("--------------------------------------------")
            errcounter += 1
    # ceck defined areas
    print("--------------------------------------------")
    print("Check defined areas")
    for item in DEFAREASARR:
        east_lv95 = int(item.split("-")[0]) * 1000
        north_lv95 = int(item.split("-")[1]) * 1000
        if check(east_lv95, north_lv95, csvdata, kmldict, True):
            print("Coord LV95 E {} N {} is OK".format(east_lv95, north_lv95))
        else:
            print("--------------------------------------------")
            print("Coord LV95 E {} N {} is Not OK".format(east_lv95, north_lv95))
            print("--------------------------------------------")
            errcounter += 1
    print("--------------------------------------------")
    print("Found {} errors".format(errcounter))


if __name__ == "__main__":
    run()
