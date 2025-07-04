# -*- coding: utf-8 -*-

"""
Simple logging utility with timestamped output.
"""
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def log_info(message):
    logging.info(message)


def log_warning(message):
    logging.warning(message)


def log_error(message):
    logging.error(message)
