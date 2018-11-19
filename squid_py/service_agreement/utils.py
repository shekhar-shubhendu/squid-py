import os
import pathlib
import json

from squid_py.ddo import PUBLIC_KEY_STORE_TYPE_HEX
from squid_py.ddo.authentication import Authentication
from squid_py.ddo.public_key_base import PublicKeyBase
from squid_py.ddo.public_key_rsa import PUBLIC_KEY_TYPE_RSA
from squid_py.keeper.utils import get_contract_by_name, get_fingerprint_by_name
from squid_py.service_agreement.service_agreement_template import ServiceAgreementTemplate
from squid_py.service_agreement.service_types import ServiceTypes
from squid_py.utils import network_name
from squid_py.utils.utilities import get_publickey_from_address


def get_sla_template_path(service_type=ServiceTypes.ASSET_ACCESS):
    if service_type == ServiceTypes.ASSET_ACCESS:
        name = 'access_sla_template.json'
    elif service_type == ServiceTypes.CLOUD_COMPUTE:
        name = 'compute_sla_template.json'
    elif service_type == ServiceTypes.FITCHAIN_COMPUTE:
        name = 'fitchain_sla_template.json'
    else:
        raise ValueError('Invalid/unsupported service agreement type "%s"' % service_type)

    os.path.join(os.path.sep, *os.path.realpath(__file__).split(os.path.sep)[1:-1], 'access_sla_template.json')

    return os.path.join(pathlib.Path.cwd(), 'squid_py', 'service_agreement', name)


def get_sla_template_dict(path):
    with open(path) as template_file:
        return json.load(template_file)


def register_service_agreement_template(keeper, owner_address, sla_template_instance=None, sla_template_path=None):
    if sla_template_instance is None:
        if sla_template_path is None:
            raise AssertionError('Invalid arguments, a template instance or a template json path is required.')

        sla_template_instance = ServiceAgreementTemplate.from_json_file(sla_template_path)

    _network_name = network_name(keeper.web3)
    contract_addresses = [
        get_contract_by_name(keeper.contract_path, _network_name, cond.contract_name)['address']
        for cond in sla_template_instance.conditions
    ]
    fingerprints = [
        get_fingerprint_by_name(
            get_contract_by_name(keeper.contract_path, _network_name, cond.contract_name)['abi'],
            cond.function_name
        )
        for i, cond in enumerate(sla_template_instance.conditions)
    ]
    fulfillment_indices = [i for i, cond in enumerate(sla_template_instance.conditions) if cond.is_terminal]
    keys = []
    for i, address in enumerate(contract_addresses):
        f = fingerprints[i]
        key = keeper.web3.soliditySha3(
            ['bytes32', 'address', 'bytes4'],
            [sla_template_instance.template_id.encode(), address, f]
        ).hex()
        sla_template_instance.conditions[i].condition_key = key
        keys.append(key)

    return keeper.service_agreement.setup_agreement_template(
        sla_template_instance.template_id,
        contract_addresses, fingerprints, sla_template_instance.conditions_dependencies,
        sla_template_instance.description,
        fulfillment_indices, sla_template_instance.service_agreement_contract.fulfillment_operator,
        owner_address
    )


def make_public_key_and_authentication(did, publisher_address, web3):
    # set public key
    public_key_value = get_publickey_from_address(web3, publisher_address)
    pub_key = PublicKeyBase('keys-1', **{'value': public_key_value, 'owner': publisher_address, 'type': PUBLIC_KEY_STORE_TYPE_HEX})
    pub_key.assign_did(did)
    # set authentication
    auth = Authentication(pub_key, PUBLIC_KEY_TYPE_RSA)
    return pub_key, auth
