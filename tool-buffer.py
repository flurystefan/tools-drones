# -*- coding: utf-8 -*-
# https://s.geo.admin.ch/9f8eaede88
# toDo
# - Funktion zum überprüfen, dass bei KML INput immer EPSG 4326 steht
import logging
import os
import socket
import sys
import buffer
import helper
from buffer import ExportGRB
from io import StringIO
from datetime import datetime as dt
from argparse import ArgumentParser
from config import get_config


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
    parser = ArgumentParser(description="Buffer a polygon")
    parser.add_argument(
        "--polygon",
        "-p",
        required=True,
        help="polygon",
    )
    parser.add_argument(
        "--inputformat",
        "-if",
        default="KML",
        help="Input format",
        choices=["KML", "KMZ"]
    )
    parser.add_argument(
        "--inputepsg",
        "-iepsg",
        default=4326,
        help="EPSG Code of input datat",
        choices=[4326, 2056]
    )
    parser.add_argument(
        "--outputformat",
        "-f",
        help="Output format",
        default="KML",
        nargs="*",
        choices=["KML", "KMZ"]
    )
    parser.add_argument(
        "--windspeed",
        "-v0",
        required=True,
        help=" Maximum allowable wind speed for operation",
    )
    parser.add_argument(
        "--characteristicdimension",
        "-cd",
        required=True,
        help="Maximum UAS characteristic dimension",
    )
    parser.add_argument(
        "--heightflightgeography",
        "-hfg",
        required=True,
        help="The width of the Flight Geography is sufficient to conduct the operation in nominal conditions.",
    )
    parser.add_argument(
        "--output",
        "-o",
        required=True,
        help="Output folder",
    )

    return vars(parser.parse_args())


def downloadkml(polygon, kmlfile):
    if polygon.startswith("https://map.geo.admin.ch"):
        return helper.download(helper.get_kmlurl(polygon), kmlfile)
    elif polygon.startswith("https://s.geo.admin.ch"):
        return helper.download(helper.get_kmlurl(helper.unshortenurl(polygon)), kmlfile)
    elif os.path.isfile(polygon):
        return polygon
    else:
        logging.error("File not found {}".format(polygon))
        return None


def run(cfg, polygon, inputformat, outputfolder, outputformate, v0, cd, hfg):
    exp = None
    kmlfile = downloadkml(polygon, os.path.join(outputfolder, cfg["downloadfilename"] + ".kml"))
    if inputformat == "KML" and kmlfile:
        exp = ExportGRB(buffer.kml2gdf(kmlfile), outputfolder, v0, cd, hfg)
    elif inputformat == "KMZ":
        logging.info("Not yet implemeted")
    else:
        logging.fatal("format {} not allowed".format(inputformat))
    if "KML" in outputformate and exp:
        exp.to_kml()
    if "KMZ" in outputformate and exp:
        exp.to_kmz()


if __name__ == "__main__":
    _args = parse_args()
    _cfg = get_config()
    _log = setup_logging(loglevel=_cfg["loglevel"])
    logging.info("Python version {0}".format(sys.version))
    try:
        run(_cfg,
            _args["polygon"],
            _args["inputformat"],
            _args["output"],
            _args["outputformat"],
            float(_args["windspeed"]),
            float(_args["characteristicdimension"]),
            float(_args["heightflithgeography"]))
    except Exception as _exc:
        logging.fatal("An error occured executing checkch", exc_info=_exc)
    finally:
        logging.shutdown()
