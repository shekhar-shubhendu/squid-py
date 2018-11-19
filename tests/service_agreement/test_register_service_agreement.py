import os
import time
import unittest
import uuid

from web3 import Web3, HTTPProvider

from squid_py.config import Config
from squid_py.keeper.utils import get_fingerprint_by_name, hexstr_to_bytes
from squid_py.ocean.ocean import Ocean
from squid_py.service_agreement.register_service_agreement import (
    execute_pending_service_agreements,
    record_service_agreement,
    register_service_agreement
)
from squid_py.service_agreement.storage import get_service_agreements


CONFIG_PATH = 'config_local.ini'


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
        service_agreement_id = uuid.uuid4().hex
        did = uuid.uuid4().hex

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
        service_agreement_id = uuid.uuid4().hex
        did = uuid.uuid4().hex
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
        service_agreement_id = uuid.uuid4().hex
        did = uuid.uuid4().hex
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
            service_agreement_id.encode(),
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
        service_agreement_id = uuid.uuid4().hex
        did = uuid.uuid4().hex
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
        cls.template_id = uuid.uuid4().hex

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
        cls.dependencies = [2, 0, 4]  # lockPayment -> grantAccess -> releasePayment

        template_name = uuid.uuid4().hex.encode()
        setup_args = [
            cls.template_id.encode(),
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
                [did.encode(), did.encode()]
            ).hex(),
            self.web3.soliditySha3(
                ['bytes32', 'uint256'],
                [did.encode(), price]
            ).hex(),
            self.web3.soliditySha3(
                ['bytes32', 'uint256'],
                [did.encode(), price]
            ).hex()
        ]
        condition_keys = [
            self.web3.soliditySha3(
                ['bytes32', 'address', 'bytes4'],
                [self.template_id.encode(),
                 contract,
                 fingerprint]
            ).hex() for contract, fingerprint in zip(self.contracts, self.fingerprints)
        ]
        timeouts = [0, 0, 0]
        signature = self.web3.eth.sign(
            self.consumer,
            hexstr=self.web3.soliditySha3(
                ['bytes32', 'bytes32[]', 'bytes32[]', 'uint256[]', 'bytes32'],
                [self.template_id.encode(),
                 condition_keys,
                 hashes,
                 timeouts,
                 service_agreement_id.encode()]
            ).hex()
        ).hex()

        execute_args = [
            self.template_id.encode(),
            signature,
            self.consumer,
            hashes,
            timeouts,
            service_agreement_id.encode(),
            did.encode(),
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
        for check in range(20):
            events = flt.get_new_entries()
            if events:
                return events[0]
            time.sleep(0.5)

    def _wait_for_access_granted(self):
        flt = self.access_conditions.events.AccessGranted.createFilter(fromBlock='latest')
        for check in range(20):
            events = flt.get_new_entries()
            if events:
                return events[0]
            time.sleep(0.5)

    def _wait_for_payment_released(self):
        flt = self.payment_conditions.events.PaymentReleased.createFilter(fromBlock='latest')
        for check in range(20):
            events = flt.get_new_entries()
            if events:
                return events[0]
            time.sleep(0.5)
