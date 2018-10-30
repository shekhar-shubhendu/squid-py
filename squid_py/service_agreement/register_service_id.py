from .event_listener import watch_service_events


def register_service_id(service_definition, service_id, *args, **kwargs):
    """ Registers the given service ID in the local storage. Subscribes to the service events.
    """

    record_service_id(service_id)
    watch_service_events(service_id, service_definition, 'consumer')


def record_service_id(service_id):
    pass
