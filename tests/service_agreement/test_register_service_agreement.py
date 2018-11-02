import unittest

from web3 import Web3, HTTPProvider

from squid_py.config import Config
from squid_py.keeper.utils import get_contract_by_name, get_fingerprint_by_name
from squid_py.service_agreement.register_service_agreement import register_service_agreement
from squid_py.utils.web3_helper import Web3Helper


CONFIG_PATH = 'config_local.ini'


class TestRegisterServiceAgreement(unittest.TestCase):

    def setUp(self):
        self.config = Config(CONFIG_PATH)
        self.web3 = Web3(HTTPProvider(self.config.keeper_url))
        self.web3helper = Web3Helper(self.web3)

        self._setup_service_agreement()

    def test_register_service_agreement_subscribes_to_events(self):
        service_agreement_id = '0x1'

        register_service_agreement(
            self.web3helper,
            self.config,
            service_agreement_id,
            {
                'conditions': [{
                    'condition_key': {
                        'contract_address': self.service_agreement.address
                    },
                    'events': [{
                        'name': 'ExecuteAgreement',
                        'actor_type': 'consumer',
                        'handler': {
                            'module_name': 'payment',
                            'function_name': 'lockPayment',
                            'version': '0.1'
                        }
                    }]
                }]
            }
        )

        while True:
            time.sleep(0.5)

    def _setup_service_agreement(self):
        self.consumer = self.web3.eth.accounts[0]
        self.web3.eth.defaultAccount = self.consumer

        contract = get_contract_by_name(self.config, self.web3helper.network_name,
                                        'ServiceAgreement')
        self.service_agreement = self.web3.eth.contract(address=contract['address'],
                                                        abi=contract['abi'])

        payment_contract = get_contract_by_name(self.config, self.web3helper.network_name,
                                                'PaymentConditions')
        self.contracts = [payment_contract['address']]
        self.fingerprints = [get_fingerprint_by_name(payment_contract['abi'], 'lockPayment')]
        self.dependencies = [0]

        setup_args = [self.contracts, self.fingerprints, self.dependencies, 'test-service'.encode()]
        receipt = self.service_agreement.functions.setupAgreementTemplate(*setup_args).transact()
        tx = self.web3.eth.waitForTransactionReceipt(receipt)

        self.template_id = Web3.toHex(self.service_agreement.events.
                                      SetupAgreementTemplate().processReceipt(tx)[0].args.
                                      serviceTemplateId)

    def _execute_service_agreement(self, service_agreement_id):
        did = 'did:ocn:test-asset'
        price = 10
        hashes = [
            '0x' + self.web3.soliditySha3(
                ['bytes32', 'bytes32', 'uint256'],
                [service_agreement_id.encode(), did.encode(), price]
            ).hex()
        ]
        condition_keys = [
            '0x' + self.web3.soliditySha3(
                ['bytes32', 'address', 'bytes4'],
                [self.template_id.encode(), self.contracts[0], self.fingerprints[0]]
            ).hex()
        ]
        timeouts = [0]
        signature = self.web3.eth.sign(
            self.consumer,
            hexstr=self.web3.soliditySha3(
                ['bytes32', 'bytes32[]', 'bytes32[]', 'uint256[]', 'bytes32'],
                [self.template_id.encode(), condition_keys, hashes, timeouts, service_agreement_id]
            ).hex()
        ).hex()

        execute_args = [self.template_id.encode(), signature.encode(), self.consumer.encode(),
                        hashes, timeouts, service_agreement_id.encode(), did.encode()]
        receipt = self.service_agreement.functions.executeAgreement(*execute_args).transact()
        self.web3.eth.waitForTransactionReceipt(receipt)
