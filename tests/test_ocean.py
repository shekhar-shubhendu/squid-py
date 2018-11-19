"""
    Test ocean class

"""

import logging
import pathlib

import pytest

from squid_py.ddo.metadata import Metadata
from squid_py.did import did_generate
from squid_py.exceptions import OceanDIDNotFound
from squid_py.ocean.asset import Asset
from squid_py.service_agreement.service_agreement import ServiceAgreement
from squid_py.service_agreement.service_factory import ServiceDescriptor
from squid_py.service_agreement.service_types import ServiceTypes
from squid_py.utils.utilities import generate_new_id


def test_ocean_instance(ocean_instance):
    ocean_instance.print_config()
    assert ocean_instance.keeper.token is not None

    # There is ONE Web3 instance
    assert ocean_instance.keeper.market.web3 is ocean_instance.keeper.auth.web3 is ocean_instance.keeper.token.web3
    assert ocean_instance._web3 is ocean_instance.keeper.web3

    ocean_instance.print_config()


def test_accounts(ocean_instance):
    for address in ocean_instance.accounts:
        print(ocean_instance.accounts[address])

    # These accounts have a positive ETH balance
    for address, account in ocean_instance.accounts.items():
        assert account.ether_balance >= 0
        assert account.ocean_balance >= 0


def test_token_request(ocean_instance):
    amount = 2000

    # Get the current accounts, assign 2
    aquarius_address = list(ocean_instance.accounts)[0]
    consumer_address = list(ocean_instance.accounts)[1]

    # Start balances for comparison
    aquarius_start_eth = ocean_instance.accounts[aquarius_address].ether_balance
    aquarius_start_ocean = ocean_instance.accounts[aquarius_address].ocean_balance

    # Make requests, assert success on request
    rcpt = ocean_instance.accounts[aquarius_address].request_tokens(amount)
    ocean_instance._web3.eth.waitForTransactionReceipt(rcpt)
    rcpt = ocean_instance.accounts[consumer_address].request_tokens(amount)
    ocean_instance._web3.eth.waitForTransactionReceipt(rcpt)

    # Update and print balances
    # Ocean.accounts is a dict address: account
    for address in ocean_instance.accounts:
        print(ocean_instance.accounts[address])
    aquarius_current_eth = ocean_instance.accounts[aquarius_address].ether_balance
    aquarius_current_ocean = ocean_instance.accounts[aquarius_address].ocean_balance

    # Confirm balance changes
    assert ocean_instance.accounts[aquarius_address].get_balance().eth == aquarius_current_eth
    assert ocean_instance.accounts[aquarius_address].get_balance().ocn == aquarius_current_ocean
    assert aquarius_current_eth < aquarius_start_eth
    assert aquarius_current_ocean == aquarius_start_ocean + amount


def test_search_assets(ocean_instance):
    pass


def test_register_asset(ocean_instance):
    logging.debug("".format())
    asset_price = 100
    sample_ddo_path = pathlib.Path.cwd() / 'tests/resources/ddo' / 'ddo_sample2.json'
    assert sample_ddo_path.exists(), "{} does not exist!".format(sample_ddo_path)

    ##########################################################
    # Setup account
    ##########################################################
    publisher_address = list(ocean_instance.accounts)[0]
    publisher_acct = ocean_instance.accounts[publisher_address]

    # ensure Ocean token balance
    if publisher_acct.ocean_balance == 0:
        rcpt = publisher_acct.request_tokens(200)
        ocean_instance._web3.eth.waitForTransactionReceipt(rcpt)

    # You will need some token to make this transfer!
    assert publisher_acct.ocean_balance > 0

    ##########################################################
    # Create an Asset with valid metadata
    ##########################################################
    asset = Asset.from_ddo_json_file(sample_ddo_path)

    ######################

    # For this test, ensure the asset does not exist in Aquarius
    meta_data_assets = ocean_instance.metadata_store.list_assets()
    if asset.ddo.did in meta_data_assets:
        ocean_instance.metadata_store.get_asset_metadata(asset.ddo.did)
        ocean_instance.metadata_store.retire_asset_metadata(asset.ddo.did)

    ##########################################################
    # Register using high-level interface
    ##########################################################
    service_descriptors = [ServiceDescriptor.access_service_descriptor(asset_price, '/purchaseEndpoint', '/serviceEndpoint', 600)]
    ocean_instance.register_asset(asset.metadata, publisher_address, service_descriptors)


def test_resolve_did(ocean_instance):
    # prep ddo
    metadata = Metadata.get_example()
    publisher = list(ocean_instance.get_accounts().values())[0]
    original_ddo = ocean_instance.register_asset(
        metadata, publisher.address,
        [ServiceDescriptor.access_service_descriptor(7, '/dummy/url', '/service/endpoint', 3)]
    )

    # happy path
    did = original_ddo.did
    ddo = ocean_instance.resolve_did(did)
    original = original_ddo.as_dictionary()
    assert ddo['publicKey'] == original['publicKey']
    assert ddo['authentication'] == original['authentication']
    assert ddo['service'][:-1] == original['service'][:-1]
    # assert ddo == original_ddo.as_dictionary(), 'Resolved ddo does not match original.'

    # Can't resolve unregistered asset
    asset_id = generate_new_id()
    unregistered_did = did_generate(asset_id)
    with pytest.raises(OceanDIDNotFound, message='Expected OceanDIDNotFound error.'):
        ocean_instance.resolve_did(unregistered_did)

    # Raise error on bad did
    asset_id = '0x0123456789'
    invalid_did = did_generate(asset_id)
    with pytest.raises(ValueError, message='Expected a ValueError when resolving invalid did.'):
        ocean_instance.resolve_did(invalid_did)


def test_sign_agreement(ocean_instance, registered_ddo):
    # assumptions:
    #  - service agreement template must already be registered
    #  - asset ddo already registered

    publisher = list(ocean_instance.accounts)[0]
    consumer = list(ocean_instance.accounts)[1]

    # sign agreement using the registered asset did above
    service = registered_ddo.get_service(service_type=ServiceTypes.ASSET_ACCESS)
    assert ServiceAgreement.SERVICE_DEFINITION_ID_KEY in service.as_dictionary()
    sa = ServiceAgreement.from_service_dict(service.as_dictionary())
    service_agreement_id = ocean_instance.sign_service_agreement(registered_ddo.did, sa.sa_definition_id, consumer)
    print('got new service agreement id.')


def test_execute_agreement(ocean_instance, registered_ddo):
    pass


def test_check_permissions(ocean_instance, registered_ddo):
    pass


def test_verify_service_agreement_signature(ocean_instance, registered_ddo):
    pass
