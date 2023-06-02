# -*- coding: utf-8 -*-
import logging
import os.path
import json
import zipfile
from helper import SwisstopoReframe
from config import get_config


class CacheKM2WGS:

    def __init__(self):
        self.cfg = get_config()
        self.__cache = {}
        self.cachezipfile = os.path.join(self.cfg["LV95_WGS84_Cache_dir"],
                                         "{}.zip".format(self.cfg["LV95_WGS84_Cache_name"]))
        self.cachefile = os.path.join(self.cfg["LV95_WGS84_Cache_dir"],
                                      "{}.json".format(self.cfg["LV95_WGS84_Cache_name"]))
        self.__cache = self.__loadcache()
        self.__modifyed = False

    def cache(self):
        return self.__cache

    def get(self, key):
        if key in self.__cache:
            logging.debug("Key found")
            return self.__cache[key]
        else:
            logging.debug("Key not found")
            wgs84 = SwisstopoReframe.viceversa(int(key[:4]) * 1000, int(key[-4:]) * 1000)
            if wgs84:
                self.__cache[key] = wgs84
                self.__modifyed = True
            return wgs84

    def save(self):
        if self.__modifyed:
            with open(self.cachefile, "w") as write_file:
                json.dump(self.__cache, write_file, indent=4)
            with zipfile.ZipFile(self.cachezipfile, mode="w") as archive:
                archive.write(self.cachefile, os.path.basename(self.cachefile), compress_type=zipfile.ZIP_DEFLATED)
        os.remove(self.cachefile)

    def __loadcache(self):
        if os.path.isfile(self.cachezipfile):
            zf = zipfile.ZipFile(self.cachezipfile, "r")
            zf.extractall(self.cfg["LV95_WGS84_Cache_dir"])
            zf.close()
        if os.path.isfile(self.cachefile):
            with open(self.cachefile, "r") as read_file:
                return json.load(read_file)
        else:
            return {}

    def size(self):
        return len(self.__cache)
