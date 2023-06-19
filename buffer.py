# -*- coding: utf-8 -*-
import logging
import os
import fiona
import simplekml
import geopandas as gpd
from grb import GroundRiskBufferCalc
from helper import SwisstopoReframe
from config import get_config
from shapely.geometry import Polygon


def kml2gdf(polygon):
    if polygon.startswith("https"):
        logging.info("Not yet implemeted")
        return None
    if os.path.isfile(polygon):
        fiona.drvsupport.supported_drivers["KML"] = "rw"
        return gpd.read_file(polygon, driver="KML")


def get_ebscode_from_gdf(gdf):
    return int(gdf.crs.srs.split(":")[1])


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
        self.__buffer2056 = None
        self.__buffer4326 = None

    @property
    def gdf4326(self):
        return self.__gdf4326

    @property
    def gdf2056(self):
        if self.__gdf2056 is None:
            logging.info("Project polygon")
            polygon = Polygon(self.__4326to2056(self.__gdf4326.geometry[0]))
            self.__gdf2056 = gpd.GeoDataFrame(geometry=[polygon], crs=2056)
        return self.__gdf2056

    def buffer(self, buffer=100, cap_style="round", join_style="round"):
        self.__buffer2056 = gpd.GeoDataFrame(
            geometry=self.gdf2056.buffer(buffer, cap_style=cap_style, join_style=join_style)
        )
        logging.info("Project buffer {:0.2f} [m]".format(buffer))
        if len(self.__buffer2056.geometry) > 1:
            logging.fatal("Buffer has more than one polygon, please contact development, just first polygon used")
        polygon = Polygon(self.__2056to4326(self.__buffer2056.geometry[0]))
        self.__buffer4326 = gpd.GeoDataFrame(geometry=[polygon], crs=4326)

    def buffer_tokml(self, kmlfile, buffer_name=None):
        if self.__buffer4326 is not None:
            self.__tokml(buffer_name).save(kmlfile)
            logging.info("KML {} written".format(kmlfile))
        else:
            logging.error("No buffer to export")

    def buffer_tokmz(self, kmlfile, buffer_name=None):
        if self.__buffer4326 is not None:
            self.__tokml(buffer_name).savekmz(kmlfile)
            logging.info("KMZ {} written".format(kmlfile))
        else:
            logging.error("No buffer to export")

    def __tokml(self, buffer_name):
        kml = simplekml.Kml()
        if buffer_name:
            kml.newfolder(name=buffer_name)
        else:
            kml.newfolder(name="Buffer")
        pol = kml.newpolygon(name="Name des Buffers", description="Beschreibung des Buffers")
        boudary = []
        for pt in self.__buffer4326.geometry[0].exterior.coords:
            boudary.append(pt)
        pol.outerboundaryis = boudary
        pol.name = "Name"
        pol.style.polystyle.color = simplekml.Color.rgb(200, 200, 200)
        pol.style.polystyle.fill = 1
        return kml

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

    @staticmethod
    def __4326to2056(polygon):
        coordslv95 = []
        for point in polygon.exterior.coords:
            coordslv95.append(SwisstopoReframe.wgs84tolv95(point))
        return coordslv95

    @staticmethod
    def __2056to4326(polygon):
        coordswgs84 = []
        for point in polygon.exterior.coords:
            coordswgs84.append(SwisstopoReframe.lv95towgs84(point))
        return coordswgs84


class ExportGRB(GdfBuffer, GroundRiskBufferCalc):

    def __init__(self, gdf, output, v0, cd, hfg,
                 version="current", aircrafttype="rotorcraft", scv_name="scv", sgrb_name="sgrb"):
        GdfBuffer.__init__(self, gdf)
        GroundRiskBufferCalc.__init__(self, version, aircrafttype)
        self.scv_name = scv_name
        self.sgrb_name = sgrb_name
        self.output = output
        self.v0 = v0
        self.cd = cd
        self.hfg = hfg

    def to_kml(self):
        svc = self.get_scv(self.v0)
        sgrb = self.get_sgrb(self.v0, self.cd, self.hfg)
        logging.info("Contingency Area")
        self.buffer(svc)
        self.buffer_tokml(os.path.join(self.output, "{}.kml".format(self.scv_name)), "SVC")
        logging.info("Ground Risk Buffer")
        self.buffer(sgrb)
        self.buffer_tokml(os.path.join(self.output, "{}.kml".format(self.sgrb_name)), "SGRB")

    def to_kmz(self):
        svc = self.get_scv(self.v0)
        sgrb = self.get_sgrb(self.v0, self.cd, self.hfg)
        logging.info("Contingency Area")
        self.buffer(svc)
        self.buffer_tokmz(os.path.join(self.output, "{}.kmz".format(self.scv_name)), "SVC")
        logging.info("Ground Risk Buffer")
        self.buffer(sgrb)
        self.buffer_tokmz(os.path.join(self.output, "{}.kmz".format(self.sgrb_name)), "SGRB")
