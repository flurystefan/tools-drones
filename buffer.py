# -*- coding: utf-8 -*-
import logging
import os
import fiona
import geopandas as gpd
from config import get_config


class KML:

    def __init__(self, polygon, output):
        self.cfg = get_config()
        if polygon.startswith("https"):
            logging.info("Not yet implemeted")
        if os.path.isfile(polygon):
            self.geojsonfile = os.path.join(output, self.cfg["polygongeojson"])
            # gpd.io.file.fiona.drvsupport.supported_drivers['KML'] = 'rw'
            fiona.drvsupport.supported_drivers['KML'] = 'rw'
            # # Read file from KML
            data = gpd.read_file(polygon, driver="KML")
            data.to_file(self.geojsonfile, driver='GeoJSON')
            pass
