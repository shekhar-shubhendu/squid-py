

"""
Ocean Protocol DID/DDO Python Library

.. moduleauthor: Bill



"""
__author__ = """OceanProtocol"""
__version__ = '0.0.1'

from did_ddo_lib.main import (
	did_generate,
	did_split,
)

from did_ddo_lib.ocean_ddo import (
    OceanDDO,
    PUBLIC_KEY_STORE_TYPE_PEM,
    PUBLIC_KEY_STORE_TYPE_JWK,
    PUBLIC_KEY_STORE_TYPE_HEX,
    PUBLIC_KEY_STORE_TYPE_BASE64,
)
