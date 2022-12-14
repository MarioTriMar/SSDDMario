"""Submodule containing the CLI command handlers."""

import logging
import sys

from iceflix.main import MainApp
from iceflix.catalog import Catalog

LOG_FORMAT = '%(asctime)s - %(levelname)-7s - %(module)s:%(funcName)s:%(lineno)d - %(message)s'


def setup_logging():
    """Configure the logging."""
    logging.basicConfig(
        level=logging.DEBUG,
        format=LOG_FORMAT,
    )


def main_service():
    """Handles the `mainservice` CLI command."""
    setup_logging()
    logging.info("Main service starting...")
    sys.exit(MainApp().main(sys.argv))


def catalog_service():
    """Handles the `catalogservice` CLI command."""
    setup_logging()
    logging.info("Main service starting...")
    catalog=Catalog()
    return (catalog.main(sys.argv))


def file_service():
    """Handles the `streamingservice` CLI command."""
    setup_logging()
    logging.info("File service")
    return 0


def authentication_service():
    """Handles the `authenticationservice` CLI command."""
    setup_logging()
    logging.info("Authentication service")
    return 0


def client():
    """Handles the IceFlix client CLI command."""
    setup_logging()
    logging.info("Starting IceFlix client...")
    return 0
