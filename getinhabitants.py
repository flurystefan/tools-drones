# -*- coding: utf-8 -*-
import logging


class STACInhabitants:

    def __init__(self, collection, asset_key, url, created, updated, timeofdata, epsg, checksum):
        self.collection_name = collection
        self.asset_key = asset_key
        self.url = url
        self.created = created
        self.updated = updated
        self.timeofdata = timeofdata
        self.epsg = epsg
        self.checksum =checksum


class STACAPIInhabitants:

    def __init__(self, collection):
        self.__collection = collection
        self.__items = self.__collection.get_items()
        self.__sortet_items = sorted(self.__items, key=lambda x: x.datetime, reverse=True)
        self.first_item = self.__sortet_items[0]



    def get_assets_of_first_item(self):
        assets = self.get_first_item().assets
