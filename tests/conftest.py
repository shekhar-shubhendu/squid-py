import os

import pytest

from squid_py.ocean.ocean import Ocean


@pytest.fixture
def ocean_instance():
    path_config = 'config_local.ini'
    os.environ['CONFIG_FILE'] = path_config
    ocean = Ocean(os.environ['CONFIG_FILE'])

    return ocean
