import os
import pathlib

import pytest

from squid_py.ddo.metadata import Metadata
from squid_py.ocean.ocean import Ocean
from squid_py.service_agreement.service_factory import ServiceDescriptor


@pytest.fixture
def ocean_instance():
    path_config = 'config_local.ini'
    os.environ['CONFIG_FILE'] = path_config
    ocean = Ocean(os.environ['CONFIG_FILE'])

    return ocean
