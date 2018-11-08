import sqlite3

from .event_listener import watch_service_agreement_events


def register_service_agreement(web3, contract_path, storage_path, account, service_agreement_id,
                               did, service_definition, actor_type, num_confirmations=12):
    """ Registers the given service agreement in the local storage.
        Subscribes to the service agreement events.
    """

    record_service_agreement(storage_path, service_agreement_id, did)
    watch_service_agreement_events(web3, contract_path, account, service_agreement_id,
                                   service_definition, actor_type, num_confirmations)


def record_service_agreement(storage_path, service_agreement_id, did):
    """ Records the given pending service agreement.
    """
    conn = sqlite3.connect(storage_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            'CREATE TABLE IF NOT EXISTS service_agreements (id VARCHAR PRIMARY KEY, did VARCHAR);'
        )
        cursor.execute(
            'INSERT OR REPLACE INTO service_agreements VALUES (?,?);',
            [service_agreement_id, did],
        )
        conn.commit()
    finally:
        conn.close()


def get_pending_service_agreements(storage_path):
    conn = sqlite3.connect(storage_path)
    try:
        cursor = conn.cursor()
        return [row for row in cursor.execute('SELECT * FROM service_agreements;')]
    finally:
        conn.close()
