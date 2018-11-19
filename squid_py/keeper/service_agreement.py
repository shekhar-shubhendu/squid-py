from squid_py.config import DEFAULT_GAS_LIMIT
from squid_py.keeper.contract_base import ContractBase
from web3 import Web3

from squid_py.keeper.utils import hexstr_to_bytes
import uuid

class ServiceAgreement(ContractBase):
    """
    """
    SERVICE_AGREEMENT_ID = 'serviceAgreementId'

    def __init__(self, web3, contract_path):
        ContractBase.__init__(self, web3, contract_path, 'ServiceAgreement')
        self._defaultGas = DEFAULT_GAS_LIMIT

    def setup_agreement_template(self, template_id, contracts, fingerprints, dependencies_bits,
                                 service_description, fulfillment_indices, fulfillment_operator, owner_address):
        assert isinstance(service_description, str) and service_description.strip() != '', 'bad service description.'
        assert contracts and isinstance(contracts, list), 'contracts arg: expected list, got {0}'.format(type(contracts))
        assert fingerprints and isinstance(fingerprints, list), 'fingerprints arg: expected list, got {0}'.format(type(fingerprints))
        assert dependencies_bits and isinstance(dependencies_bits, list), 'dependencies_bits arg: expected list, got {0}'.format(type(dependencies_bits))

        service_bytes = Web3.toHex(Web3.sha3(text=service_description))
        _contracts = [self.to_checksum_address(contr) for contr in contracts]
        _fingerprints = [hexstr_to_bytes(self.web3, f) for f in fingerprints]
        receipt = self.contract_concise.setupAgreementTemplate(
            template_id,
            _contracts,
            _fingerprints,
            dependencies_bits,
            service_bytes,
            fulfillment_indices,
            fulfillment_operator,
            transact={'from': owner_address, 'gas': DEFAULT_GAS_LIMIT}
        )
        tx = self.web3.eth.waitForTransactionReceipt(receipt)
        result = self.events.SetupAgreementTemplate().processReceipt(tx)
        print('result::::: ', result)
        return tx

    def execute_service_agreement(self, template_id, signature, consumer, hashes, timeouts, service_agreement_id, did_id, publisher):
        receipt = self.contract_concise.executeAgreement(
            template_id, signature, consumer, hashes, timeouts, service_agreement_id, did_id,
            transact={'from': publisher, 'gas': DEFAULT_GAS_LIMIT}
        )
        self.web3.eth.waitForTransactionReceipt(receipt)
        return receipt

    def fulfill_agreement(self, service_agreement_id):
        self.contract_concise.fulfillAgreement(service_agreement_id)

    def get_template_status(self, sa_template_id):
        return self.contract_concise.getTemplateStatus(sa_template_id)

    def revoke_agreement_template(self, sa_template_id):
        self.contract_concise.revokeAgreementTemplate(sa_template_id)
        return True

    def get_template_owner(self, sa_template_id):
        return self.contract_concise.getTemplateOwner(sa_template_id)

    def get_template_id(self, service_agreement_id):
        return self.contract_concise.getTemplateId(service_agreement_id)

    def get_agreement_status(self, service_agreement_id):
        return self.contract_concise.getAgreementStatus(service_agreement_id)

    def get_service_agreement_publisher(self, service_agreement_id):
        return self.contract_concise.getAgreementPublisher(service_agreement_id)

    def get_service_agreement_consumer(self, service_agreement_id):
        return self.contract_concise.getServiceAgreementConsumer(service_agreement_id)

    def get_condition_by_fingerprint(self, service_agreement_id, contract_address, function_fingerprint):
        return self.contract_concise.getConditionByFingerprint(service_agreement_id, contract_address, function_fingerprint)
