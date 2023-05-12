# -*- coding: utf-8 -*-
import logging
from urllib import request
import os
import hashlib
import simplekml
from gridcache import CacheKM2WGS
import pandas as pd


class STACResidents:

    def __init__(self, collection, asset_key, href_url, created, updated, timeofdata, epsg, checksum):
        self.collection_name = collection
        self.asset_key = asset_key
        self.url = href_url
        self.created = created
        self.updated = updated
        self.timeofdata = timeofdata
        self.epsg = epsg
        self.checksum = checksum


class STACapiResidents:
    CSVHEADERLINE = '"RELI";"E_KOORD";"N_KOORD";"NUMMER";"CLASS"\n'

    def __init__(self, collection):
        self.__collection = collection
        self.__items = self.__collection.get_items()
        self.__sortet_items = sorted(self.__items, key=lambda x: x.datetime, reverse=True)
        self.first_item = self.__sortet_items[0]
        self.__first_item_assets = self.first_item.assets
        self.first_asset_key, self.first_asset_data = next(iter(self.__first_item_assets.items()))
        self.stac_inhabitants = STACResidents(
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
                    return filename
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
                        if len(linarr) != 5 \
                                or str(linarr[0]) != "{}{}".format(linarr[1][1:5], linarr[2][1:5]) \
                                or not linarr[3].isdigit():
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


class KmResidents:
    DF_COLS = ["KEY_LB", "number_of_residents", "CLASS", "RGB",
               "E_LB", "N_LB", "easting_LB", "northing_LB",
               "E_LT", "N_LT", "easting_LT", "northing_LT",
               "E_RT", "N_RT", "easting_RT", "northing_RT",
               "E_RB", "N_RB", "easting_RB", "northing_RB"]

    def __init__(self, csv, grouping):
        self.__csv = csv
        self.kmdict, self.residents = self.__sumkm()
        self.__df = self.__todf(grouping)

    def tokml(self, kmlfile):
        if os.path.isfile(kmlfile):
            os.remove(kmlfile)
        self.__getkml().save(kmlfile)
        logging.info("KML {} written".format(kmlfile))

    def tokmz(self, kmzfile):
        if os.path.isfile(kmzfile):
            os.remove(kmzfile)
        self.__getkml().savekmz(kmzfile)
        logging.info("KML {} written".format(kmzfile))

    def tocsv(self, csvfile):
        self.__df.to_csv(csvfile, sep=";", index=False)
        logging.info("CSV {} written".format(csvfile))

    def toxlsx(self, xlsxfile):
        with pd.ExcelWriter(xlsxfile, engine="openpyxl") as writer:
            self.__df.to_excel(writer, sheet_name="residents per km2", index=False)
        logging.info("XLSX {} written".format(xlsxfile))

    def __getkml(self):
        kml = simplekml.Kml()
        kml.newfolder(name="Population (residents) per km^2")
        for row in self.__df.itertuples():
            colarr = row.RGB.split(",")
            pol = kml.newpolygon(name=row.number_of_residents,
                                 description="Number of residents : {}".format(row.number_of_residents))
            pol.outerboundaryis = [(row.easting_LB, row.northing_LB),
                                   (row.easting_LT, row.northing_LT),
                                   (row.easting_RT, row.northing_RT),
                                   (row.easting_RB, row.northing_RB)]
            pol.style.polystyle.color = simplekml.Color.rgb(int(colarr[0]), int(colarr[1]), int(colarr[2]))
            pol.style.polystyle.fill = 1
        return kml

    def __todf(self, grouping):
        groupingdict = self.__getlimitdict(grouping)
        df = pd.DataFrame(columns=self.DF_COLS)
        tilecache = CacheKM2WGS()
        counter = 0
        for k, v in self.kmdict.items():
            if counter % 1000 == 0:
                logging.info("{} of {}".format(len(self.kmdict), counter))
            counter += 1
            lbe_lv95 = int(k[:4])
            lbn_lv95 = int(k[4:])
            lbe_wgs, lbn_wgs = tilecache.get(k)
            lte_wgs, ltn_wgs = tilecache.get("{}{}".format(lbe_lv95 + 1, lbn_lv95))
            rte_wgs, rtn_wgs = tilecache.get("{}{}".format(lbe_lv95 + 1, lbn_lv95 + 1))
            rbe_wgs, rbn_wgs = tilecache.get("{}{}".format(lbe_lv95, lbn_lv95 + 1))
            classid, rgb = self.__getcol(v, groupingdict)
            list_row = [k, v, "<={}".format(classid), rgb,
                        lbe_lv95 * 1000, lbn_lv95 * 1000, lbe_wgs, lbn_wgs,
                        int(lbe_lv95 + 1) * 1000, lbn_lv95 * 1000, lte_wgs, ltn_wgs,
                        int(lbe_lv95 + 1) * 1000, int(lbn_lv95 + 1) * 1000, rte_wgs, rtn_wgs,
                        lbe_lv95 * 1000, int(lbn_lv95 + 1) * 1000, rbe_wgs, rbn_wgs]
            df.loc[len(df)] = list_row
        tilecache.save()
        return df

    @staticmethod
    def __getcol(residents, groupingdict):
        for k, v in groupingdict.items():
            if residents <= k:
                return k, v

    @staticmethod
    def __getlimitdict(grouping):
        gdict = {int(k): v for k, v in grouping.items()}
        return {k: gdict[k] for k in sorted(gdict)}

    def __sumkm(self):
        kmdict = {}
        residents = 0
        with open(self.__csv) as csv:
            lines = csv.readlines()
            for idx in range(1, len(lines)):
                linarr = lines[idx].split(";")
                key = "{}{}".format(linarr[1][:4], linarr[2][:4])
                val = int(linarr[3])
                residents += val
                if key in kmdict:
                    kmdict[key] += val
                else:
                    kmdict[key] = val
        return kmdict, residents
