from .event_listener import watch_service_agreement_events


def register_service_agreement(web3, config, service_agreement_id, service_definition,
                               *args, **kwargs):
    """ Registers the given service agreement in the local storage.
        Subscribes to the service agreement events.
    """

    record_service_agreement(service_agreement_id)
    watch_service_agreement_events(web3, config, service_agreement_id,
                                   service_definition, 'consumer')


def record_service_agreement(service_agreement_id):
    pass
