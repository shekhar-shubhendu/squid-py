from squid_py.service_agreement.service_agreement_condition import ServiceAgreementCondition


class ServiceAgreementTemplate(object):
    DOCUMENT_TYPE = 'OceanProtocolServiceAgreementTemplate'
    TEMPLATE_ID_KEY = 'slaTemplateId'

    def __init__(self, template_json=None):
        self.template_id = ''
        self.name = ''
        self.description = ''
        self.creator = ''
        self.conditions = []
        if template_json:
            self.parse_template_json(template_json)

    def parse_template_json(self, template_json):
        assert template_json['type'] == self.DOCUMENT_TYPE, ''
        self.template_id = template_json['templateId']
        self.name = template_json['name']
        self.description = template_json['description']
        self.creator = template_json['creator']
        self.conditions = [ServiceAgreementCondition(cond_json) for cond_json in template_json['conditions']]
