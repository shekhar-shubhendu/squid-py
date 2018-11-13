import sqlite3

from .event_listener import (
    watch_service_agreement_events,
    watch_service_agreement_fulfilled
)


def register_service_agreement(web3, contract_path, storage_path, account, service_agreement_id,
                               did, service_definition, actor_type, num_confirmations=12):
    """ Registers the given service agreement in the local storage.
        Subscribes to the service agreement events.
    """

    def _cleanup(event):
        record_service_agreement(storage_path, service_agreement_id, did, 'fulfilled')

    watch_service_agreement_fulfilled(web3, contract_path, service_agreement_id, service_definition,
                                      _cleanup, num_confirmations=num_confirmations)

    record_service_agreement(storage_path, service_agreement_id, did)
    watch_service_agreement_events(web3, contract_path, account, service_agreement_id,
                                   service_definition, actor_type, num_confirmations)


def record_service_agreement(storage_path, service_agreement_id, did, status='pending'):
    """ Records the given pending service agreement.
    """
    conn = sqlite3.connect(storage_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS service_agreements
               (id VARCHAR PRIMARY KEY, did VARCHAR, status VARCHAR(10));'''
        )
        cursor.execute(
            'INSERT OR REPLACE INTO service_agreements VALUES (?,?,?)',
            [service_agreement_id, did, status],
        )
        conn.commit()
    finally:
        conn.close()


def get_service_agreements(storage_path, status='pending'):
    conn = sqlite3.connect(storage_path)
    try:
        cursor = conn.cursor()
        return [row for row in
                cursor.execute("SELECT * FROM service_agreements WHERE status='%s';" % status)]
    finally:
        conn.close()


def execute_pending_service_agreements(web3, contract_path, storage_path, account, actor_type,
                                       did_resolver_fn, num_confirmations=12):
    """ Iterates over pending service agreements recorded in the local storage,
        fetches their service definitions, and subscribes to service agreement events.
    """
    for service_agreement_id, did, _ in get_service_agreements(storage_path):
        ddo = did_resolver_fn(did)
        for service_definition in ddo['service']:
            if service_definition['type'] != 'Access':
                continue

            watch_service_agreement_events(web3, contract_path, account, service_agreement_id,
                                           service_definition, actor_type,
                                           num_confirmations=num_confirmations)
