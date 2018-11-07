import time
import unittest
import uuid

from web3 import Web3, HTTPProvider

from squid_py.config import Config
from squid_py.keeper.utils import get_fingerprint_by_name, hexstr_to_bytes
from squid_py.ocean import Ocean
from squid_py.service_agreement.register_service_agreement import register_service_agreement


CONFIG_PATH = 'config_local.ini'


class TestRegisterServiceAgreement(unittest.TestCase):

    def setUp(self):
        self.config = Config(CONFIG_PATH)
        self.web3 = Web3(HTTPProvider(self.config.keeper_url))

        self.ocean = Ocean(CONFIG_PATH)
        self.market = self.ocean.keeper.market
        self.token = self.ocean.keeper.token
        self.payment_conditions = self.ocean.keeper.payment_conditions
        self.service_agreement = self.ocean.keeper.service_agreement

        self.consumer = self.web3.eth.accounts[0]
        self.web3.eth.defaultAccount = self.consumer

        self._setup_service_agreement()
        self._setup_token()

    def test_register_service_agreement_subscribes_to_events(self):
        service_agreement_id = uuid.uuid4().hex
 
        did = uuid.uuid4().hex
        price = 10

        lock_payment_fingerprint = get_fingerprint_by_name(
            self.payment_conditions.contract.abi,
            'lockPayment',
        )
        register_service_agreement(
            self.web3,
            self.config.keeper_path,
            self.consumer,
            service_agreement_id,
            {
                'conditions': [{
                    'conditionKey': {
                        'contractAddress': self.service_agreement.contract.address
                    },
                    'events': [{
                        'name': 'ExecuteAgreement',
                        'actorType': 'consumer',
                        'handler': {
                            'moduleName': 'payment',
                            'functionName': 'lockPayment',
                            'version': '0.1'
                        }
                    }]
                }, {
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
            },
            'consumer'
        )

        self._execute_service_agreement(service_agreement_id, did, price)

        flt = self.payment_conditions.events.PaymentLocked.createFilter(fromBlock='latest')
        for check in range(10):
            events = flt.get_new_entries()
            if events:
                break
            time.sleep(0.5)

        assert events, 'Expected PaymentLocked to be emitted'

    def _setup_service_agreement(self):
        self.contracts = [self.payment_conditions.contract.address]
        self.fingerprints = [
            hexstr_to_bytes(
                self.web3,
                get_fingerprint_by_name(self.payment_conditions.contract.abi, 'lockPayment'),
            )
        ]
        self.dependencies = [0]

        template_name = uuid.uuid4().hex.encode()
        setup_args = [self.contracts, self.fingerprints, self.dependencies, template_name]
        receipt = self.service_agreement.contract_concise.setupAgreementTemplate(
            *setup_args,
            transact={'from': self.consumer}
        )
        tx = self.web3.eth.waitForTransactionReceipt(receipt)

        self.template_id = Web3.toHex(self.service_agreement.events.
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

    def _setup_token(self):
        self.market.contract_concise.requestTokens(100, transact={'from': self.consumer})

        self.token.contract_concise.approve(
            self.payment_conditions.address,
            100,
            transact={'from': self.consumer},
        )
