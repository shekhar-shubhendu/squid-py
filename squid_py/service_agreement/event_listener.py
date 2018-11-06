import importlib

from squid_py.keeper.utils import get_contract_abi_by_address
from squid_py.utils import watch_event


def watch_service_agreement_events(web3, config, service_agreement_id, service_definition,
                                   actor_type, num_confirmations=12):
    """ Subscribes to the events defined in the given service definition, targeted
        for the given actor type. Filters events by the given service agreement ID.

        The service definition format is described in OEP-11.
    """

    filters = {'serviceId': service_agreement_id.encode()}
    for condition in service_definition['conditions']:
        for event in condition['events']:
            if event['actor_type'] != actor_type:
                continue

            event_handler = event['handler']
            version = event_handler['version'].replace('.', '_')
            import_path = 'squid_py.modules.v{}.{}'.format(version, event_handler['module_name'])
            module = importlib.import_module(import_path, 'squid_py')
            fn = getattr(module, event_handler['function_name'])

            def _callback(payload):
                fn(service_agreement_id, service_definition, payload)

            contract_address = condition['condition_key']['contract_address']
            contract_abi = get_contract_abi_by_address(config, contract_address)
            contract = web3.eth.contract(address=contract_address,
                                                    abi=contract_abi)

            watch_event(
                contract,
                event['name'],
                _callback,
                fromBlock='latest',
                interval=0.5,
                filters=filters
            )
