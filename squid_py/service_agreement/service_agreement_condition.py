
class Parameter:
    def __init__(self, param_json):
        self.name = param_json['name']
        self.type = param_json['type']
        self.value = param_json['value']


class ServiceAgreementCondition(object):
    def __init__(self, condition_json=None):
        self.name = ''
        self.contract_address = ''
        self.function_fingerprint = ''
        self.function_name = ''
        self.dependencies = []
        self.timeout_flags = []
        self.parameters = []
        self.timeout = 0

    def parse_condition_json(self, condition_json):
        self.name = condition_json['name']
        self.timeout = condition_json['timeout']
        self.contract_address = condition_json['conditionKey']['contractAddress']
        self.function_fingerprint = condition_json['conditionKey']['fingerprint']
        self.function_name = condition_json['conditionKey']['functionName']
        self.dependencies = condition_json['dependencies']
        self.timeout_flags = condition_json['timeoutFlags']
        assert len(self.dependencies) == len(self.timeout_flags)
        if self.dependencies:
            assert sum(self.timeout_flags) == 0 or self.timeout > 0, 'timeout must be set when any dependency is set to rely on a timeout.'

        self.parameters = [Parameter(p) for p in condition_json['parameters']]
