import os
import time
import unittest
import uuid

from web3 import Web3, HTTPProvider

from squid_py.config import Config
from squid_py.keeper.utils import get_fingerprint_by_name, hexstr_to_bytes
from squid_py.ocean import Ocean
from squid_py.service_agreement.register_service_agreement import (
    get_service_agreements,
    register_service_agreement
)


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
        cls.service_agreement = cls.ocean.keeper.service_agreement

        cls.consumer = cls.web3.eth.accounts[0]
        cls.web3.eth.defaultAccount = cls.consumer

        cls._setup_service_agreement()
        cls._setup_token()

        cls.storage_path = 'test_squid_py.db'

    def tearDown(self):
        os.remove(self.storage_path)

    def get_simple_service_agreement_definition(self, did, price):
        lock_payment_fingerprint = get_fingerprint_by_name(
            self.payment_conditions.contract.abi,
            'lockPayment',
        )
        return {
            'serviceAgreementContract': {
                'address': self.service_agreement.contract.address,
                'events': [{
                    'name': 'ExecuteAgreement',
                    'actorType': 'consumer',
                    'handler': {
                        'moduleName': 'payment',
                        'functionName': 'lockPayment',
                        'version': '0.1'
                    }
                }]
            },
            'conditions': [{
                'conditionKey': {
                    'contractAddress': self.payment_conditions.contract.address,
                    'fingerprint': lock_payment_fingerprint,
                    'functionName': 'lockPayment'
                },
                'parameters': {
                    'did': did,
                    'price': price,
                },
                'events': []
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
                    'address': self.service_agreement.contract.address,
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

        flt = self.payment_conditions.events.PaymentLocked.createFilter(fromBlock='latest')
        for check in range(20):
            events = flt.get_new_entries()
            if events:
                break
            time.sleep(0.5)

        assert events, 'Expected PaymentLocked to be emitted'

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

        self._execute_service_agreement(service_agreement_id, did, price)

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

    @classmethod
    def _setup_service_agreement(cls):
        cls.contracts = [cls.payment_conditions.contract.address]
        cls.fingerprints = [
            hexstr_to_bytes(
                cls.web3,
                get_fingerprint_by_name(cls.payment_conditions.contract.abi, 'lockPayment'),
            )
        ]
        cls.dependencies = [0]

        template_name = uuid.uuid4().hex.encode()
        setup_args = [cls.contracts, cls.fingerprints, cls.dependencies, template_name]
        receipt = cls.service_agreement.contract_concise.setupAgreementTemplate(
            *setup_args,
            transact={'from': cls.consumer}
        )
        tx = cls.web3.eth.waitForTransactionReceipt(receipt)

        cls.template_id = Web3.toHex(cls.service_agreement.events.
                                     SetupAgreementTemplate().processReceipt(tx)[0].args.
                                     serviceTemplateId)

    def _execute_service_agreement(self, service_agreement_id, did, price):
        hashes = [
            self.web3.soliditySha3(
                ['bytes32', 'uint256'],
                [did.encode(), price]
            ).hex()
        ]
        condition_keys = [
            self.web3.soliditySha3(
                ['bytes32', 'address', 'bytes4'],
                [hexstr_to_bytes(self.web3, self.template_id),
                 self.contracts[0],
                 self.fingerprints[0]]
            ).hex()
        ]
        timeouts = [0]
        signature = self.web3.eth.sign(
            self.consumer,
            hexstr=self.web3.soliditySha3(
                ['bytes32', 'bytes32[]', 'bytes32[]', 'uint256[]', 'bytes32'],
                [hexstr_to_bytes(self.web3, self.template_id),
                 condition_keys,
                 hashes,
                 timeouts,
                 service_agreement_id.encode()]
            ).hex()
        ).hex()

        execute_args = [
            hexstr_to_bytes(self.web3, self.template_id),
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
