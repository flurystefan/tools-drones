# -*- coding: utf-8 -*-
import logging
import requests
from config import get_config
from urllib.parse import urlparse, unquote

KMLSTARTSTRING = "KML||https:"


class SwisstopoReframe:

    @staticmethod
    def lv95towgs84(e, n=None):
        return SwisstopoReframe.viceversa(e, n)

    @staticmethod
    def wgs84tolv95(e, n=None):
        return SwisstopoReframe.viceversa(e, n)

    @staticmethod
    def viceversa(e, n=None, to=None):
        rettuple = False
        if n is None:
            e, n = e
            rettuple = True
        if to is None:
            if 5.0 < e < 11.0 and 45.0 < n < 48.0:
                to = "LV95"
            elif 2400000.0 < e < 2900000 and 1000000 < n < 1400000:
                to = "WGS84"
            else:
                raise ValueError("coords not in allowed range")
        if to not in ["WGS84", "LV95"]:
            raise ValueError("to {} not in list {}".format(to, ["WGS84", "LV95"]))
        try:
            cfg = get_config()
            if to == "WGS84":
                logging.debug("WGS84 long {}, lat {}".format(e, n))
            else:
                logging.debug("WGS84 long {}, lat {}".format(e, n))
            for idx in range(cfg["maxtriesReframe"]):
                params = {"easting": e, "northing": n, "format": "json"}
                if to == "WGS84":
                    response = requests.get(cfg["ReframeLV95ToWGS84"], params=params)
                else:
                    response = requests.get(cfg["ReframeWGS84ToLV95"], params=params)
                if response.status_code == 200:
                    # Request was successful
                    data = response.json()
                    if to == "WGS84":
                        logging.debug("WGS84 easting {}, northing {}".format(data["easting"], data["northing"]))
                    else:
                        logging.debug("LV95 easting {}, northing {}".format(data["easting"], data["northing"]))
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


def get_kmlurl(url):
    paresd_url = urlparse(url)
    parameters = paresd_url.query
    decoded_parameters = unquote(parameters)
    if decoded_parameters.find(KMLSTARTSTRING) > 0:
        helper = decoded_parameters[decoded_parameters.index(KMLSTARTSTRING) + 5:].split("&")
        return "{}{}".format(helper[0], helper[1])


def unshortenurl(shortened_url):
    try:
        response = requests.get(shortened_url)
        return response.url
    except Exception:
        raise
