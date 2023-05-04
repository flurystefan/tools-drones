# -*- coding: utf-8 -*-
# ch.bfs.volkszaehlung-gebaeudestatistik_gebaeude
# https://pystac.readthedocs.io/en/stable/quickstart.html
# https://pystac-client.readthedocs.io/en/stable/quickstart.html
import socket
import os
import logging
import sys
from io import StringIO
from argparse import ArgumentParser
from datetime import datetime as dt
from pystac_client import Client


def setup_logging(folder=None):
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

        logging.basicConfig(
            level=logging.INFO,
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
        help="Collection oder layer id auf geo.admin.ch",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output folder",
    )
    return vars(parser.parse_args())


def run():
    """ Main routine """
    # client = Client.open("https://earth-search.aws.element84.com/v0")
    client = Client.open("https://data.geo.admin.ch/api/stac/v0.9")
    print()


if __name__ == "__main__":
    _args = parse_args()
    _log = setup_logging()
    logging.info("Python version {0}".format(sys.version))
    try:
        run()
    except Exception as _exc:
        logging.fatal("An error occured executing checkch", exc_info=_exc)
    finally:
        logging.shutdown()
