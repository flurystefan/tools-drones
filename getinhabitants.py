# -*- coding: utf-8 -*-
import logging
from urllib import request
import os
import hashlib


class STACInhabitants:

    def __init__(self, collection, asset_key, href_url, created, updated, timeofdata, epsg, checksum):
        self.collection_name = collection
        self.asset_key = asset_key
        self.url = href_url
        self.created = created
        self.updated = updated
        self.timeofdata = timeofdata
        self.epsg = epsg
        self.checksum = checksum


class STACapiInhabitants:
    CSVHEADERLINE = '"RELI";"E_KOORD";"N_KOORD";"NUMMER";"CLASS"\n'

    def __init__(self, collection):
        self.__collection = collection
        self.__items = self.__collection.get_items()
        self.__sortet_items = sorted(self.__items, key=lambda x: x.datetime, reverse=True)
        self.first_item = self.__sortet_items[0]
        self.__first_item_assets = self.first_item.assets
        self.first_asset_key, self.first_asset_data = next(iter(self.__first_item_assets.items()))
        self.stac_inhabitants = STACInhabitants(
            collection.title,
            self.first_asset_key,
            self.first_asset_data.href,
            self.first_asset_data.extra_fields["created"],
            self.first_asset_data.extra_fields["updated"],
            self.first_item.datetime,
            self.first_asset_data.extra_fields["proj:epsg"],
            self.first_asset_data.extra_fields["checksum:multihash"]
        )

    def download(self, folder=os.path.dirname(__file__)):
        logging.info("Start to downlaod {} from {}".format(self.stac_inhabitants.asset_key, self.stac_inhabitants.url))
        try:
            filename = os.path.join(folder, self.stac_inhabitants.asset_key)
            if os.path.isfile(filename):
                file_hash = self.__get_filehash(filename)
                if file_hash == self.stac_inhabitants.checksum:
                    logging.info("File already downloaded and checksum is ok")
                    return None
                else:
                    logging.info("File outdated")
                    os.remove(filename)
                    return self.__download(filename)
            else:
                logging.info("File not found")
                return self.__download(filename)
        except Exception as e:
            logging.error("Download failed {}".format(e))
            return None

    @staticmethod
    def __get_filehash(filename):
        # https://multiformats.io/multihash/
        with open(filename, "rb") as f:
            file_bytes = f.read()
            file_hash = hashlib.sha256(file_bytes)
            hash_val = file_hash.hexdigest()
            return "12{}{}".format(format(file_hash.digest_size, "x"), hash_val)

    def __download(self, filename):
        request.urlretrieve(self.stac_inhabitants.url, filename)
        file_hash = self.__get_filehash(filename)
        if file_hash == self.stac_inhabitants.checksum:
            logging.info("Download succeeded and checksum ok")
            with open(filename) as csv:
                lines = csv.readlines()
                if lines[0] == self.CSVHEADERLINE:
                    for idx in range(1, len(lines)):
                        linarr = lines[idx].split(";")
                        if len(linarr) != 5 or str(linarr[0]) != "{}{}".format(linarr[1][1:5], linarr[2][1:5]):
                            logging.error("Error found on line {} in csv".format(idx))
                            return None
                    logging.info("Checked {} lines in csv".format(idx))
                else:
                    logging.error("CSV Header {} ist not ok ({})".format(lines[0], self.CSVHEADERLINE))
            logging.info("Schema check ok")
            return filename
        else:
            logging.error("Check checksum failed")
            logging.info(file_hash)
            logging.info(self.stac_inhabitants.checksum)
            return None
