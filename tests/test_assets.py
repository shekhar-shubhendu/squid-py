"""
    Test ocean class
"""

import logging
import os
from squid_py import Ocean


def test_load():
    ocean = Ocean(os.environ['config_local.ini'])

