
from squid_py.service_agreement.utils import get_condition_value_hash


class ServiceAgreement(object):
    SERVICE_DEFINITION_ID_KEY = 'serviceDefinitionId'
    SERVICE_CONDITIONS_KEY = 'conditions'

    def __init__(self, sa_definition_id, conditions):
        self.sa_definition_id = sa_definition_id
        self.conditions = conditions

    def as_dict(self):
        return {
            ServiceAgreement.SERVICE_DEFINITION_ID_KEY: self.sa_definition_id,
            ServiceAgreement.SERVICE_CONDITIONS_KEY: [cond.as_dict() for cond in self.conditions]
        }

    @property
    def conditions_params_value_hashes(self):
        value_hashes = []
        for cond in self.conditions:
            value_hashes.append(get_condition_value_hash(cond.param_types, cond.param_values))

        return value_hashes

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
