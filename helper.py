# -*- coding: utf-8 -*-
import logging
import requests
from config import get_config


class SwisstopoReframe:

    @staticmethod
    def lv95towgs84(e, n=None):
        rettuple = False
        if n is None:
            e, n = e
            rettuple = True
        try:
            cfg = get_config()
            logging.debug("LV95 E {}, N {}".format(e, n))
            for idx in range(cfg["maxtriesReframe"]):
                params = {"easting": e, "northing": n, "format": "json"}
                response = requests.get(cfg["ReframeLV95ToWGS84"], params=params)
                if response.status_code == 200:
                    # Request was successful
                    data = response.json()
                    logging.debug("WGS84 long {}, lat {}".format(data["easting"], data["northing"]))
                    if rettuple:
                        return data["easting"], data["northing"]
                    else:
                        return [data["easting"], data["northing"]]
                else:
                    logging.error(
                        "Request failed with status code: {} at {} {} try: {}".format(response.status_code, e, n, idx)
                    )
        except Exception as ex:
            logging.error("Max tries to reframe reached, return coord 0,0. Errormsg = {}".format(ex))
            return None

    @staticmethod
    def wgs84tolv95(e, n=None):
        rettuple = False
        if n is None:
            e, n = e
            rettuple = True
        try:
            cfg = get_config()
            logging.debug("WGS84 long {}, lat {}".format(e, n))
            for idx in range(cfg["maxtriesReframe"]):
                params = {"easting": e, "northing": n, "format": "json"}
                response = requests.get(cfg["ReframeWGS84ToLV95"], params=params)
                if response.status_code == 200:
                    # Request was successful
                    data = response.json()
                    logging.debug("WGS84 easting {}, northing {}".format(data["easting"], data["northing"]))
                    if rettuple:
                        return data["easting"], data["northing"]
                    else:
                        return [data["easting"], data["northing"]]
                else:
                    logging.error(
                        "Request failed with status code: {} at {} {} try: {}".format(response.status_code, e, n, idx)
                    )
        except Exception as ex:
            logging.error("Max tries to reframe reached, return coord 0,0. Errormsg = {}".format(ex))
            return None
