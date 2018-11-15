from web3 import Web3

from squid_py.service_agreement.service_agreement_template import ServiceAgreementTemplate


class ServiceAgreement(object):
    SERVICE_DEFINITION_ID_KEY = 'serviceDefinitionId'
    SERVICE_CONTRACT_KEY = 'serviceAgreementContract'
    SERVICE_CONDITIONS_KEY = 'conditions'
    PURCHASE_ENDPOINT_KEY = 'purchaseEndpoint'
    SERVICE_ENDPOINT_KEY = 'serviceEndpoint'

    def __init__(self, sa_definition_id, sla_template_id, conditions, service_agreement_contract, purchase_endpoint=None, service_endpoint=None):
        self.sa_definition_id = sa_definition_id
        self.sla_template_id = sla_template_id
        self.conditions = conditions
        self.service_agreement_contract = service_agreement_contract
        self.purchase_endpoint = purchase_endpoint
        self.service_endpoint = service_endpoint


    @property
    def conditions_params_value_hashes(self):
        value_hashes = []
        for cond in self.conditions:
            value_hashes.append(cond.values_hash)

        return value_hashes

    @property
    def conditions_timeouts(self):
        return [cond.timeout for cond in self.conditions]

    @property
    def conditions_keys(self):
        return [cond.condition_key for cond in self.conditions]

    @property
    def conditions_contracts(self):
        return [cond.contract_address for cond in self.conditions]

    @property
    def conditions_fingerprints(self):
        return [cond.function_fingerprint for cond in self.conditions]

    @property
    def conditions_dependencies(self):
        name_to_i = {cond.name: i for i, cond in enumerate(self.conditions)}
        i_to_name = {i: cond.name for i, cond in enumerate(self.conditions)}
        for i, cond in enumerate(self.conditions):
            dep = []
            for j in range(len(self.conditions)):
                if i == j:
                    dep.append(0)
                elif self.conditions[j].name in cond.dependencies:
                    dep.append(1)
        # TODO:

        return

    @classmethod
    def from_service_dict(cls, service_dict):
        return cls(
            service_dict[cls.SERVICE_DEFINITION_ID_KEY], service_dict[ServiceAgreementTemplate.TEMPLATE_ID_KEY],
            service_dict[cls.SERVICE_CONDITIONS_KEY], service_dict[cls.SERVICE_CONTRACT_KEY],
            service_dict.get(cls.PURCHASE_ENDPOINT_KEY), service_dict.get(cls.SERVICE_ENDPOINT_KEY)
        )

    @staticmethod
    def generate_service_agreement_hash(sa_template_id, condition_keys, values_hash_list, timeouts, service_agreement_id, did_id):
        return Web3.soliditySha3(
            ['bytes32', 'bytes32[]', 'bytes32[]', 'bytes32[]', 'bytes32', 'bytes32'],
            [sa_template_id, condition_keys, values_hash_list, timeouts, service_agreement_id, did_id]
        )

    def get_signed_agreement_hash(self, web3, did_id, service_agreement_id, consumer):
        """

        :param web3: Object -- instance of web3.Web3 to use for signing the message
        :param did_id: str -- the *id* portion of the asset did
        :param service_agreement_id: hex str -- a new service agreement id for this service transaction
        :param consumer: hex str -- address of consumer to sign the message with

        :return: signed_msg_hash, msg_hash
        """
        agreement_hash = ServiceAgreement.generate_service_agreement_hash(
            self.sla_template_id, self.conditions_keys, self.conditions_params_value_hashes, self.conditions_timeouts, service_agreement_id, did_id
        )
        return web3.eth.sign(consumer, agreement_hash), agreement_hash

    def as_dictionary(self):
        return {
            ServiceAgreement.SERVICE_DEFINITION_ID_KEY: self.sa_definition_id,
            ServiceAgreementTemplate.TEMPLATE_ID_KEY: self.sla_template_id,
            ServiceAgreement.SERVICE_CONTRACT_KEY: self.service_agreement_contract.as_dictionary(),
            ServiceAgreement.SERVICE_CONDITIONS_KEY: [cond.as_dictionary() for cond in self.conditions]
        }

