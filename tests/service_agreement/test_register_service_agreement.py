import os
import time
import unittest
import uuid

from web3 import Web3, HTTPProvider

from squid_py.config import Config
from squid_py.keeper.utils import get_fingerprint_by_name, hexstr_to_bytes, get_contract_abi_and_address
from squid_py.ocean.ocean import Ocean
from squid_py.service_agreement.register_service_agreement import (
    execute_pending_service_agreements,
    record_service_agreement,
    register_service_agreement
)
from squid_py.service_agreement.storage import get_service_agreements
from squid_py.service_agreement.utils import build_condition_key
from squid_py.utils import get_network_name
from squid_py.utils.utilities import generate_new_id

CONFIG_PATH = 'config_local.ini'
NUM_WAIT_ITERATIONS = 20


class TestRegisterServiceAgreement(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.config = Config(CONFIG_PATH)
        cls.web3 = Web3(HTTPProvider(cls.config.keeper_url))

        cls.ocean = Ocean(CONFIG_PATH)
        cls.market = cls.ocean.keeper.market
        cls.token = cls.ocean.keeper.token
        cls.payment_conditions = cls.ocean.keeper.payment_conditions
        cls.access_conditions = cls.ocean.keeper.access_conditions
        cls.service_agreement = cls.ocean.keeper.service_agreement

        cls.consumer = cls.web3.eth.accounts[0]
        cls.web3.eth.defaultAccount = cls.consumer

        cls._setup_service_agreement()
        cls._setup_token()

        cls.storage_path = 'test_squid_py.db'

    def tearDown(self):
        os.remove(self.storage_path)

    def get_simple_service_agreement_definition(self, did, price):
        grant_access_fingerprint = get_fingerprint_by_name(
            self.access_conditions.contract.abi,
            'grantAccess',
        )
        lock_payment_fingerprint = get_fingerprint_by_name(
            self.payment_conditions.contract.abi,
            'lockPayment',
        )
        release_payment_fingerprint = get_fingerprint_by_name(
            self.payment_conditions.contract.abi,
            'releasePayment',
        )
        return {
            'type': 'Access',
            'templateId': self.template_id,
            'serviceAgreementContract': {
                'contractName': 'ServiceAgreement',
                'events': [{
                    'name': 'ExecuteAgreement',
                    'actorType': 'consumer',
                    'handler': {
                        'moduleName': 'payment',
                        'functionName': 'lockPayment',
                        'version': '0.1'
                    }
                }],
            },
            'conditions': [{
                'name': 'lockPayment',
                'conditionKey': "",
                'contractName': 'PaymentConditions',
                'functionName': 'lockPayment',
                'parameters': [
                    {
                        'name': 'did',
                        'type': 'byte32',
                        'value': did,
                    },
                    {
                        'name': 'price',
                        'type': 'uint256',
                        'value': price,
                    }
                ],
                'events': [{
                    'name': 'PaymentLocked',
                    'actorType': 'publisher',
                    'handler': {
                        'moduleName': 'accessControl',
                        'functionName': 'grantAccess',
                        'version': '0.1'
                    }
                }],
            }, {
                'name': 'grantAccess',
                'conditionKey': "",
                'contractName': 'AccessConditions',
                'functionName': 'grantAccess',
                'parameters': [
                    {
                        'name': 'did',
                        'type': 'byte32',
                        'value': did,
                    },
                    {
                        'name': 'price',
                        'type': 'uint256',
                        'value': price,
                    }
                ],
                'events': [{
                    'name': 'AccessGranted',
                    'actorType': 'publisher',
                    'handler': {
                        'moduleName': 'payment',
                        'functionName': 'releasePayment',
                        'version': '0.1'
                    }
                }],
            }, {
                'name': 'releasePayment',
                'conditionKey': "",
                'contractName': 'PaymentConditions',
                'functionName': 'releasePayment',
                'parameters': [
                    {
                        'name': 'did',
                        'type': 'byte32',
                        'value': did,
                    },
                    {
                        'name': 'price',
                        'type': 'uint256',
                        'value': price,
                    }
                ],
                'events': [],
            }]
        }

    def test_register_service_agreement_stores_the_record(self):
        service_agreement_id = '0x%s' % generate_new_id()
        did = '0x%s' % generate_new_id()

        register_service_agreement(
            self.web3,
            self.config.keeper_path,
            self.storage_path,
            self.consumer,
            service_agreement_id,
            did,
            {
                'serviceAgreementContract': {
                    'contractName': 'ServiceAgreement',
                    'events': []
                },
                'conditions': []
            },
            'consumer',
        )

        expected_agreements = [(service_agreement_id, did, 'pending')]
        assert expected_agreements == get_service_agreements(self.storage_path)

    def test_register_service_agreement_subscribes_to_events(self):
        service_agreement_id = '0x%s' % generate_new_id()
        did = '0x%s' % generate_new_id()
        price = 10

        register_service_agreement(
            self.web3,
            self.config.keeper_path,
            self.storage_path,
            self.consumer,
            service_agreement_id,
            did,
            self.get_simple_service_agreement_definition(did, price),
            'consumer',
            num_confirmations=1
        )

        self._execute_service_agreement(service_agreement_id, did, price)
        payment_locked = self._wait_for_payment_locked()
        assert payment_locked, 'Expected PaymentLocked to be emitted'

    def test_register_service_agreement_updates_fulfilled_agreements(self):
        service_agreement_id = '0x%s' % generate_new_id()
        did = '0x%s' % generate_new_id()
        price = 10

        register_service_agreement(
            self.web3,
            self.config.keeper_path,
            self.storage_path,
            self.consumer,
            service_agreement_id,
            did,
            self.get_simple_service_agreement_definition(did, price),
            'consumer',
            num_confirmations=0
        )

        register_service_agreement(
            self.web3,
            self.config.keeper_path,
            self.storage_path,
            self.consumer,  # using the same account for the sake of simplicity here
            service_agreement_id,
            did,
            self.get_simple_service_agreement_definition(did, price),
            'publisher',
            num_confirmations=0
        )

        self._execute_service_agreement(service_agreement_id, did, price)

        payment_locked = self._wait_for_payment_locked()
        assert payment_locked, 'Payment was not locked'

        access_granted = self._wait_for_access_granted()
        assert access_granted, 'Access was not granted'

        payment_released = self._wait_for_payment_released()
        assert payment_released, 'Payment was not released'

        receipt = self.service_agreement.contract_concise.fulfillAgreement(
            service_agreement_id,
            transact={'from': self.consumer},
        )
        self.web3.eth.waitForTransactionReceipt(receipt)

        expected_agreements = [(service_agreement_id, did, 'fulfilled')]
        for i in range(10):
            agreements = get_service_agreements(self.storage_path, 'fulfilled')
            if expected_agreements == agreements:
                break

            time.sleep(0.5)

        assert expected_agreements == agreements
        assert not get_service_agreements(self.storage_path)

    def test_execute_pending_service_agreements_subscribes_to_events(self):
        service_agreement_id = '0x%s' % generate_new_id()
        did = '0x%s' % generate_new_id()
        price = 10

        record_service_agreement(self.storage_path, service_agreement_id, did)

        def _did_resolver_fn(did):
            return {
                'service': [
                    self.get_simple_service_agreement_definition(did, price),
                ]
            }

        execute_pending_service_agreements(
            self.web3,
            self.config.keeper_path,
            self.storage_path,
            self.consumer,
            'consumer',
            _did_resolver_fn,
            num_confirmations=0,
        )

        self._execute_service_agreement(service_agreement_id, did, price)

        flt = self.payment_conditions.events.PaymentLocked.createFilter(fromBlock='latest')
        for check in range(10):
            events = flt.get_new_entries()
            if events:
                break
            time.sleep(0.5)

        assert events, 'Expected PaymentLocked to be emitted'

    @classmethod
    def _setup_service_agreement(cls):
        cls.template_id = '0x%s' % generate_new_id()
        cls.contract_names = [cls.access_conditions.name, cls.payment_conditions.name, cls.payment_conditions.name]
        cls.contract_abis = [
            cls.access_conditions.contract.abi,
            cls.payment_conditions.contract.abi,
            cls.payment_conditions.contract.abi
        ]
        cls.contracts = [
            cls.access_conditions.contract.address,
            cls.payment_conditions.contract.address,
            cls.payment_conditions.contract.address,
        ]
        cls.fingerprints = [
            hexstr_to_bytes(
                cls.web3,
                get_fingerprint_by_name(cls.access_conditions.contract.abi, 'grantAccess'),
            ),
            hexstr_to_bytes(
                cls.web3,
                get_fingerprint_by_name(cls.payment_conditions.contract.abi, 'lockPayment'),
            ),
            hexstr_to_bytes(
                cls.web3,
                get_fingerprint_by_name(cls.payment_conditions.contract.abi, 'releasePayment'),
            )
        ]
        # lockPayment -> grantAccess -> releasePayment
        # 4, 8           1, 2           16, 32
        cls.dependencies = [4, 0, 1]

        template_name = uuid.uuid4().hex.encode()
        setup_args = [
            cls.template_id,
            cls.contracts,
            cls.fingerprints,
            cls.dependencies,
            template_name,
            [0],  # root condition
            0,  # AND
        ]
        receipt = cls.service_agreement.contract_concise.setupAgreementTemplate(
            *setup_args,
            transact={'from': cls.consumer}
        )
        cls.web3.eth.waitForTransactionReceipt(receipt)

    def _execute_service_agreement(self, service_agreement_id, did, price):
        hashes = [
            self.web3.soliditySha3(
                ['bytes32', 'bytes32'],
                [did, did]
            ).hex(),
            self.web3.soliditySha3(
                ['bytes32', 'uint256'],
                [did, price]
            ).hex(),
            self.web3.soliditySha3(
                ['bytes32', 'uint256'],
                [did, price]
            ).hex()
        ]
        condition_keys = [
            self.web3.soliditySha3(
                ['bytes32', 'address', 'bytes4'],
                [self.template_id,
                 contract,
                 fingerprint]
            ).hex() for contract, fingerprint in zip(self.contracts, self.fingerprints)
        ]
        function_names = ['grantAccess', 'lockPayment', 'releasePayment']
        _network_name = get_network_name(self.web3)
        for i, key in enumerate(condition_keys):
            fn_name = function_names[i]
            abi, address = get_contract_abi_and_address(self.web3, self.ocean.keeper.contract_path, self.contract_names[i], _network_name)
            assert abi == self.contract_abis[i], 'abi does not match.'
            assert address == self.contracts[i], 'address does not match'
            f = hexstr_to_bytes(self.web3, get_fingerprint_by_name(abi, fn_name))
            assert f == self.fingerprints[i], 'fingerprint mismatch %s vs %s' % (f, self.fingerprints[i])
            _key = build_condition_key(self.web3, self.contracts[i], f, self.template_id)
            assert _key == key, 'condition key does not match: %s vs %s' % (_key, key)

        timeouts = [0, 0, 0]
        signature = self.web3.eth.sign(
            self.consumer,
            hexstr=self.web3.soliditySha3(
                ['bytes32', 'bytes32[]', 'bytes32[]', 'uint256[]', 'bytes32'],
                [self.template_id,
                 condition_keys,
                 hashes,
                 timeouts,
                 service_agreement_id]
            ).hex()
        ).hex()

        execute_args = [
            self.template_id,
            signature,
            self.consumer,
            hashes,
            timeouts,
            service_agreement_id,
            did,
        ]
        self.service_agreement.contract_concise.executeAgreement(
            *execute_args,
            transact={'from': self.consumer}
        )

    @classmethod
    def _setup_token(cls):
        cls.market.contract_concise.requestTokens(100, transact={'from': cls.consumer})

        cls.token.contract_concise.approve(
            cls.payment_conditions.address,
            100,
            transact={'from': cls.consumer},
        )

    def _wait_for_payment_locked(self):
        flt = self.payment_conditions.events.PaymentLocked.createFilter(fromBlock='latest')
        for check in range(NUM_WAIT_ITERATIONS):
            events = flt.get_new_entries()
            if events:
                return events[0]
            time.sleep(0.5)

    def _wait_for_access_granted(self):
        flt = self.access_conditions.events.AccessGranted.createFilter(fromBlock='latest')
        for check in range(NUM_WAIT_ITERATIONS):
            events = flt.get_new_entries()
            if events:
                return events[0]
            time.sleep(0.5)

    def _wait_for_payment_released(self):
        flt = self.payment_conditions.events.PaymentReleased.createFilter(fromBlock='latest')
        for check in range(NUM_WAIT_ITERATIONS):
            events = flt.get_new_entries()
            if events:
                return events[0]
            time.sleep(0.5)
