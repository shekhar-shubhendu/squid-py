from squid_py.ddo import DDO
from squid_py.service_agreement.service_agreement_condition import ServiceAgreementCondition


class AssetDDO(DDO):

    @property
    def did(self):
        return

    @property
    def sa_template_id(self):
        return

    @property
    def get_service_conditions(self):
        services = self['services']
        conditions = services['conditions']
        conditions = [ServiceAgreementCondition(cond) for cond in conditions]
        return conditions