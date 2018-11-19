from squid_py.service_agreement.utils import get_sla_template_dict, get_sla_template_path


def test_setup_service_agreement_template(ocean_instance):
    template_dict = get_sla_template_dict(get_sla_template_path())
    tx_receipt = ocean_instance._register_service_agreement_template(template_dict, list(ocean_instance.accounts)[0])

    # verify new sa template is registered

