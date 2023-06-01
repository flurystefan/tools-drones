# -*- coding: utf-8 -*-
# https://s.geo.admin.ch/9f8eaede88
# toDo
# - Funktion zum überprüfen, dass bei KML INput immer EPSG 4326 steht
import logging
import os
import socket
import sys
import buffer
from buffer import GdfBuffer
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
        "--output",
        "-o",
        required=True,
        help="Output folder",
    )
    parser.add_argument(
        "--outputformat",
        "-of",
        help="Output format",
        default="KML",
        nargs="*",
        choices=["KML", "KMZ"]
    )
    return vars(parser.parse_args())


def run(polygon, inputformat, outputfolder):
    if inputformat == "KML":
        gdf = buffer.kml2gdf(polygon)
        gdfb = GdfBuffer(gdf)
        gdfb.buffer(20)
        gdfb.buffer_tokml(outputfolder)
    elif inputformat == "KMZ":
        logging.info("Not yet implemeted")
    else:
        logging.fatal("format {} not allowed".format(inputformat))


if __name__ == "__main__":
    _args = parse_args()
    _cfg = get_config()
    _log = setup_logging(loglevel=_cfg["loglevel"])
    logging.info("Python version {0}".format(sys.version))
    try:
        run(_args["polygon"], _args["inputformat"], _args["output"])
    except Exception as _exc:
        logging.fatal("An error occured executing checkch", exc_info=_exc)
    finally:
        logging.shutdown()