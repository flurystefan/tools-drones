# -*- coding: utf-8 -*-
import logging
import os
import fiona
import geopandas as gpd
from helper import SwisstopoReframe
from config import get_config
from shapely.geometry import Polygon


def __kml2geojson(polygon, output):
    cfg = get_config()
    if polygon.startswith("https"):
        logging.info("Not yet implemeted")
    if os.path.isfile(polygon):
        geojsonfile = os.path.join(output, cfg["polygongeojson"])
        # gpd.io.file.fiona.drvsupport.supported_drivers['KML'] = 'rw'
        fiona.drvsupport.supported_drivers['KML'] = 'rw'
        # # Read file from KML
        data = gpd.read_file(polygon, driver="KML")

        coords = [(2600000, 1200000), (2601000, 1200000), (2601000, 1201000), (2600000, 1201000)]
        polygon = Polygon(coords)
        data2056 = gpd.GeoDataFrame(geometry=[polygon], crs=2056)
        data2056.to_file(geojsonfile, driver='GeoJSON')

        # data2056.to_file(geojsonfile, driver='GeoJSON')
        buffer = data2056.buffer(100, cap_style="round", join_style="round")
        buffer.to_file(geojsonfile, driver='GeoJSON')

        bufferwgs84 = buffer.to_crs(4326)
        bufferwgs84.to_file(r"D:\git\tools-drones\temp\buffer.kml", driver="KML")


class GdfBuffer:

    def __init__(self, gdf):
        self.cfg = get_config()
        if not self.__checkgdf(gdf):
            raise TypeError("See logfile")
        else:
            if get_ebscode_from_gdf(gdf) == 2056:
                self.__gdf2056 = gdf
                self.__gdf4326 = None
            else:
                self.__gdf2056 = None
                self.__gdf4326 = gdf


    @property
    def gdf4326(self):
        return self.__gdf4326

    @property
    def gdf2056(self):
        return self.__gdf2056

    def __checkgdf(self, gdf):
        msg = ""
        if str(get_ebscode_from_gdf(gdf)) not in self.cfg["epscodes"].keys():
            msg += "SRS {} not in list {} ".fromat(get_ebscode_from_gdf(gdf), self.cfg["epscodes"].keys())
        if len(gdf.geometry) != 1:
            msg += "to many [{}] polygons, just one polygon allowed ".fromat(len(gdf.geometry))
        else:
            if gdf.geometry[0].geom_type != "Polygon":
                msg += "geometry {} not allowed".format(gdf.geometry[0].geom_type)
        if len(msg) == 0:
            return True
        else:
            logging.fatal(msg)
            return False


def kml2gdf(polygon, output):
    cfg = get_config()
    if polygon.startswith("https"):
        logging.info("Not yet implemeted")
        return None
    if os.path.isfile(polygon):
        fiona.drvsupport.supported_drivers["KML"] = "rw"
        return gpd.read_file(polygon, driver="KML")


def __kml2gdf(polygon, output):
    cfg = get_config()
    if polygon.startswith("https"):
        logging.info("Not yet implemeted")
    if os.path.isfile(polygon):
        fiona.drvsupport.supported_drivers["KML"] = "rw"
        kmldata = gpd.read_file(polygon, driver="KML")
        coordslv95 = []
        if len(kmldata.geometry) == 1:
            if kmldata.geometry[0].geom_type == "Polygon":
                polygon = kmldata.geometry[0]
                for point in polygon.exterior.coords:
                    coordslv95.append(SwisstopoReframe.wgs84tolv95(point))
            else:
                print("Wrong geometry type")
        else:
            print("To many polygons, just one polygon allowed")

    geojsonfile = os.path.join(output, cfg["polygongeojson"])
    polygon = Polygon(coordslv95)
    data2056 = gpd.GeoDataFrame(geometry=[polygon], crs=2056)
    data2056.to_file(geojsonfile, driver='GeoJSON')
    return data2056


def get_ebscode_from_gdf(gdf):
    return int(gdf.crs.srs.split(":")[1])

def buffergdf(gdf, buffer=100, cap_style="round", join_style="round"):
    return gdf.buffer(buffer, cap_style="round", join_style="round")

