# -*- coding: utf-8 -*-
# ch.bfs.volkszaehlung-gebaeudestatistik_gebaeude
# https://pystac-client.readthedocs.io/en/stable/quickstart.html
import socket
import os
import logging
import sys
from getresidents import STACapiResidents, KmResidents
from config import get_config
from io import StringIO
from argparse import ArgumentParser
from datetime import datetime as dt
from pystac_client import Client


def setup_logging(folder=None, loglevel="INFO"):
    """ Setup logging

    Returns:
        StringIO string buffer of the log
    """
    try:
        filename = "{:%Y%m%d-%H%M%S}_{}_{}.log".format(
            dt.now(),
            socket.gethostname(),
            os.path.splitext(os.path.basename(__file__))[0],
        )
        log_string = StringIO()
        handlers = [
            logging.StreamHandler(sys.stdout),
            logging.StreamHandler(log_string),
        ]
        if folder is not None:
            handlers.append(logging.FileHandler(filename=os.path.join(folder, filename)))

        logger_levels = {
            'ERROR': logging.ERROR,
            'INFO': logging.INFO,
            'DEBUG': logging.DEBUG
        }
        logging.basicConfig(
            level=logger_levels[loglevel],
            format="%(asctime)s [{}] [{}] [%(threadName)s] [%(levelname)s]  %(message)s".format(
                socket.gethostname(), os.path.basename(sys.argv[0][:-3])
            ),
            handlers=handlers,
        )
        return log_string
    except Exception as exc:
        print("Error setting up logging", exc)
        raise


def parse_args():
    """ Parse CLI args

    Returns:
        Dictionary of parsed args
    """
    parser = ArgumentParser(description="Get data from STAC API map.geo.admin.ch")
    parser.add_argument(
        "--collection",
        "-c",
        required=True,
        help="Collection oder layer id auf geo.admin.ch",
    )
    parser.add_argument(
        "--output",
        "-o",
        required=True,
        help="Output folder",
    )
    parser.add_argument(
        "--format",
        "-f",
        required=True,
        help="Output folder",
        nargs="*",
        choices=["KML", "KMZ", "CSV", "XLSX"]
    )

    return vars(parser.parse_args())


def run(cfg, key, outputpath, formate):
    """ Main routine """
    client = Client.open(cfg["STAC_url"])
    logging.info("STAC {}".format(client.description))
    collection = client.get_collection(key)

    inh = STACapiResidents(collection)
    csv = inh.download(outputpath)
    if csv:
        logging.info("File {} downloaded".format(csv))
    km = KmResidents(csv, cfg["grouping"])
    if "KML" in formate:
        km.tokml(os.path.join(outputpath, cfg["kmlfilename"]))
    if "KMZ" in formate:
        km.tokmz(os.path.join(outputpath, cfg["kmzfilename"]))
    if "CSV" in formate:
        km.tocsv(os.path.join(outputpath, cfg["csvfilename"]))
    if "XLSX" in formate:
        km.toxlsx(os.path.join(outputpath, cfg["xlsxfilename"]))


if __name__ == "__main__":
    _args = parse_args()
    _cfg = get_config()
    _log = setup_logging(loglevel=_cfg["loglevel"])
    logging.info("Python version {0}".format(sys.version))
    try:
        run(_cfg, _args["collection"], _args["output"], _args["format"])
    except Exception as _exc:
        logging.fatal("An error occured executing checkch", exc_info=_exc)
    finally:
        logging.shutdown()
