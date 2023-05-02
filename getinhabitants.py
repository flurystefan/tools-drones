# -*- coding: utf-8 -*-
import pystac
import logging
import sys
import argparse


def parse_args():
    pass


def run():
    pass


if __name__ == "__main__":
    """ Entrypoint for the application """
    try:
        logging.basicConfig(level="INFO")
        logging.info("Python version {}".format(sys.version))
    except Exception as _err:
        logging.fatal("Could not initialise logging. Script will exit.", exc_info=_err)
        sys.exit(1)

    try:
        _args = parse_args()
        run()
        logging.info("Got file from STAC")
    except Exception as _err:
        logging.fatal("Anlayse failed", exc_info=_err)
        sys.exit(1)
    finally:
        logging.shutdown()
