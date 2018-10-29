

"""
Ocean Protocol DID/DDO Python Library

.. moduleauthor: Bill



"""
__author__ = """Ocean Protocol Foundation"""
__version__ = '0.0.1'

from did_ddo_lib.main import (
    did_generate,
    did_generate_from_ddo,
    did_validate,
    did_parse,
    is_did_valid,
    did_generate_from_id,
    get_id_from_did,
)

from did_ddo_lib.ocean_ddo import (
    OceanDDO,
)

from did_ddo_lib.public_key_base import (
    PUBLIC_KEY_STORE_TYPE_PEM,
    PUBLIC_KEY_STORE_TYPE_HEX,
    PUBLIC_KEY_STORE_TYPE_BASE64,
    PUBLIC_KEY_STORE_TYPE_BASE85,
)
