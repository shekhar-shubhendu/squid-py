from squid_py.ocean import Ocean
from squid_py.asset import Asset

import logging
import json
import pathlib

# Load samples
SAMPLE_METADATA_PATH = pathlib.Path.cwd() / 'tests/resources/metadata' / 'sample_metadata1.json'
assert SAMPLE_METADATA_PATH.exists(), "{} does not exist!".format(SAMPLE_METADATA_PATH)
with open(SAMPLE_METADATA_PATH) as f:
    SAMPLE_METADATA1 = json.load(f)

SAMPLE_METADATA_PATH = pathlib.Path.cwd() / 'tests/resources/metadata' / 'sample_metadata2.json'
assert SAMPLE_METADATA_PATH.exists(), "{} does not exist!".format(SAMPLE_METADATA_PATH)
with open(SAMPLE_METADATA_PATH) as f:
    SAMPLE_METADATA2 = json.load(f)

# Disable low level loggers
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("web3").setLevel(logging.WARNING)

