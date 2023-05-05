# -*- coding: utf-8 -*-
# ch.bfs.volkszaehlung-gebaeudestatistik_gebaeude
# https://pystac.readthedocs.io/en/stable/quickstart.html
# https://pystac-client.readthedocs.io/en/stable/quickstart.html
import socket
import os
import logging
import sys
from getinhabitants import STACAPIInhabitants
from config import get_config
from io import StringIO
from argparse import ArgumentParser
from datetime import datetime as dt
from pystac_client import Client
from urllib import request


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
    return vars(parser.parse_args())


def run(cfg, key, outputpath):
    """ Main routine """
    # client = Client.open("https://earth-search.aws.element84.com/v0")
    client = Client.open(cfg["STAC_url"])
    logging.info("STAC {}".format(client.description))
    collection = client.get_collection(key)

    inh = STACAPIInhabitants(collection)


    items = collection.get_items()
    sorted_items = sorted(items, key=lambda x: x.datetime, reverse=True)
    item = sorted_items[0]
    assets = item.assets
    first_key, first_value = next(iter(assets.items()))

    filename = first_key
    url = first_value.href
    crateted = first_value.extra_fields["created"]
    crateted = first_value.extra_fields["updated"]
    epsg = first_value.extra_fields["proj:epsg"]
    checksum = first_value.extra_fields["checksum:multihash"]
    file_name = os.path.join(outputpath, filename)

    logging.info("Start to downlaod {} from {}".format(filename, client.description))
    request.urlretrieve(url, file_name)

    logging.info("Source {}".format(url))
    logging.info("Output {}".format(file_name))


if __name__ == "__main__":
    _args = parse_args()
    _cfg = cfg = get_config()
    _log = setup_logging(loglevel=_cfg["loglevel"])
    logging.info("Python version {0}".format(sys.version))
    try:
        run(_cfg, _args["collection"], _args["output"])
    except Exception as _exc:
        logging.fatal("An error occured executing checkch", exc_info=_exc)
    finally:
        logging.shutdown()
