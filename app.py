import json
import random
import time
import uuid
from datetime import datetime

from google.cloud import pubsub_v1

from config import Config
from utilities.db_helper import execute_sql_query
from utilities.rabbit_context import RabbitContext

message_rate = int(Config.MESSAGE_RATE)  # Per second
message_weightings = {
    "RESPONDENT_AUTHENTICATED": 36,
    "SURVEY_LAUNCHED": 34,
    "RESPONSE_RECEIVED": 16,
    "RESPONSE_RECEIVED.pqrs": 1,
    "RESPONSE_RECEIVED.qm": 1,
    "RESPONSE_RECEIVED.qm_blanks": 1,
    "REFUSAL_RECEIVED": 1,
    "FULFILMENT_REQUESTED.sms": 1,
    "FULFILMENT_REQUESTED.print": 1,
    "UNDELIVERED_MAIL_REPORTED": 1,
    "FULFILMENT_CONFIRMED": 1,
    "NEW_ADDRESS_REPORTED": 1,
    "ADDRESS_NOT_VALID": 1,
    "ADDRESS_TYPE_CHANGED": 1,
    "ADDRESS_MODIFIED": 1,
    "PRINT_CASE_SELECTED": 1,
    "QUESTIONNAIRE_LINKED": 1
}
message_type_randomiser = []

test_cases = []
test_unlinked_qids = []

total_messages_to_send = int(Config.TOTAL_MESSAGES_TO_SEND)
messages_to_send = []


def prepare_randomiser():
    for key, value in message_weightings.items():
        for _ in range(value):
            message_type_randomiser.append(key)


def get_cases_from_db(num_of_cases_to_fetch=int(Config.CASES_TO_FETCH)):
    sql_query = f'''
    SELECT c.case_id, c.case_ref, c.case_type, c.address_level, c.region, c.treatment_code, u.uac, u.qid
    FROM casev2.cases c, casev2.uac_qid_link u
    WHERE u.caze_case_id = c.case_id
    LIMIT {num_of_cases_to_fetch};'''

    db_result = execute_sql_query(sql_query)

    for row in db_result:
        case = {
            "case_id": row[0],
            "case_ref": row[1],
            "case_type": row[2],
            "address_level": row[3],
            "region": row[4],
            "treatment_code": row[5],
            "uac": row[6],
            "qid": row[7]
        }

        test_cases.append(case)


def get_unadressed_qids_from_db(num_of_unaddressed_qids_to_fetch=int(Config.UNADDRESSED_QIDS_TO_FETCH)):
    sql_query = f'''
        SELECT u.uac, u.qid
        FROM casev2.uac_qid_link u
        WHERE caze_case_id IS NULL
       LIMIT {num_of_unaddressed_qids_to_fetch};'''

    db_result = execute_sql_query(sql_query)

    for row in db_result:
        uac_qid_link = {
            "uac": row[0],
            "qid": row[1]
        }

        test_unlinked_qids.append(uac_qid_link)


def prepare_respondent_authenticated(random_delay, random_case):
    message_contents = {
        "event": {
            "type": "RESPONDENT_AUTHENTICATED",
            "source": "RESPONDENT_HOME",
            "channel": "RH",
            "dateTime": f"{datetime.utcnow().isoformat()}Z",
            "transactionId": str(uuid.uuid4())
        },
        "payload": {
            "response": {
                "questionnaireId": random_case['qid'],
                "caseId": random_case['case_id']
            }
        }
    }

    message = {
        "type": "RABBIT",
        "topic": "event.response.authentication",
        "delay": random_delay,
        "message_body": json.dumps(message_contents)
    }

    messages_to_send.append(message)


def prepare_survey_launched(random_delay, random_case):
    message_contents = {
        "event": {
            "type": "SURVEY_LAUNCHED",
            "source": "CONTACT_CENTRE_API",
            "channel": "CC",
            "dateTime": f"{datetime.utcnow().isoformat()}Z",
            "transactionId": str(uuid.uuid4())
        },
        "payload": {
            "response": {
                "questionnaireId": random_case['qid'],
                "caseId": random_case['case_id'],
                "agentId": "cc_000351"
            }
        }
    }

    message = {
        "type": "RABBIT",
        "topic": "event.response.authentication",
        "delay": random_delay,
        "message_body": json.dumps(message_contents)
    }

    messages_to_send.append(message)


def prepare_response_received(random_delay, random_case):
    tx_id = str(uuid.uuid4())

    message_contents = {
        "timeCreated": f"{datetime.utcnow().isoformat()}Z",
        "metadata": {
            "case_id": random_case['case_id'],
            "tx_id": tx_id,
            "questionnaire_id": random_case['qid'],
        }
    }

    message = {
        "type": "PUBSUB_EQ",
        "topic": Config.RECEIPT_TOPIC_ID,
        "project": Config.RECEIPT_TOPIC_PROJECT,
        "delay": random_delay,
        "message_body": json.dumps(message_contents),
        "tx_id": tx_id
    }

    messages_to_send.append(message)


def prepare_response_received_pqrs(random_delay, random_case):
    prepare_response_received_pqrs_and_qm(random_delay, random_case, "PQRS")


def prepare_response_received_qm(random_delay, random_case):
    prepare_response_received_pqrs_and_qm(random_delay, random_case, "QM")


def prepare_response_received_pqrs_and_qm(random_delay, random_case, channel):
    tx_id = str(uuid.uuid4())

    message_contents = {
        "channel": channel,
        "dateTime": f"{datetime.utcnow().isoformat()}Z",
        "questionnaireId": random_case['qid'],
        "transactionId": str(uuid.uuid4()),
        "type": "RESPONSE_RECEIVED",
        "unreceipt": False
    }

    message = {
        "type": "PUBSUB",
        "topic": Config.OFFLINE_RECEIPT_TOPIC_NAME,
        "project": Config.OFFLINE_RECEIPT_TOPIC_PROJECT_ID,
        "delay": random_delay,
        "message_body": json.dumps(message_contents),
        "tx_id": tx_id
    }

    messages_to_send.append(message)


def prepare_response_received_qm_blanks(random_delay, random_case):
    tx_id = str(uuid.uuid4())

    message_contents = {
        "channel": "QM",
        "dateTime": f"{datetime.utcnow().isoformat()}Z",
        "questionnaireId": random_case['qid'],
        "transactionId": str(uuid.uuid4()),
        "type": "RESPONSE_RECEIVED",
        "unreceipt": True
    }

    message = {
        "type": "PUBSUB",
        "topic": Config.OFFLINE_RECEIPT_TOPIC_NAME,
        "project": Config.OFFLINE_RECEIPT_TOPIC_PROJECT_ID,
        "delay": random_delay,
        "message_body": json.dumps(message_contents),
        "tx_id": tx_id
    }

    messages_to_send.append(message)


def prepare_refusal_received(random_delay, random_case):
    message_contents = {
        "event": {
            "type": "REFUSAL_RECEIVED",
            "source": "CONTACT_CENTRE_API",
            "channel": "CC",
            "dateTime": f"{datetime.utcnow().isoformat()}Z",
            "transactionId": str(uuid.uuid4())
        },
        "payload": {
            "refusal": {
                "type": "HARD_REFUSAL",
                "report": "respondent unwilling",
                "agentId": "110001",
                "collectionCase": {
                    "id": random_case['case_id']
                },
                "contact": {
                    "title": "Ms",
                    "forename": "jo",
                    "surname": "smith",
                    "telNo": "+447890000000"
                },
                "address": {
                    "addressLine1": "1a main street",
                    "addressLine2": "upper upperingham",
                    "addressLine3": "",
                    "townName": "upton",
                    "postcode": "UP103UP",
                    "region": "E",
                    "uprn": "123456789"
                }
            }
        }
    }

    message = {
        "type": "RABBIT",
        "topic": "event.respondent.refusal",
        "delay": random_delay,
        "message_body": json.dumps(message_contents)
    }

    messages_to_send.append(message)


def prepare_fulfilment_requested_sms(random_delay, random_case):
    message_contents = {
        "event": {
            "type": "FULFILMENT_REQUESTED",
            "source": "CONTACT_CENTRE_API",
            "channel": "CC",
            "dateTime": f"{datetime.utcnow().isoformat()}Z",
            "transactionId": str(uuid.uuid4())
        },
        "payload": {
            "fulfilmentRequest": {
                "fulfilmentCode": "UACHHT1",
                "caseId": random_case['case_id'],
                "address": {},
                "contact": {
                    "telNo": "+447876224123"
                }
            }
        }
    }

    message = {
        "type": "RABBIT",
        "topic": "event.fulfilment.request",
        "delay": random_delay,
        "message_body": json.dumps(message_contents)
    }

    messages_to_send.append(message)


def prepare_fulfilment_requested_print(random_delay, random_case):
    message_contents = {
        "event": {
            "type": "FULFILMENT_REQUESTED",
            "source": "CONTACT_CENTRE_API",
            "channel": "CC",
            "dateTime": f"{datetime.utcnow().isoformat()}Z",
            "transactionId": str(uuid.uuid4())
        },
        "payload": {
            "fulfilmentRequest": {
                "fulfilmentCode": "P_OR_H1",
                "caseId": random_case['case_id'],
                "address": {},
                "contact": {
                }
            }
        }
    }

    message = {
        "type": "RABBIT",
        "topic": "event.fulfilment.request",
        "delay": random_delay,
        "message_body": json.dumps(message_contents)
    }

    messages_to_send.append(message)


def prepare_fulfilment_confirmed(random_delay, random_case):
    message_contents = {
        "dateTime": f"{datetime.utcnow().isoformat()}Z",
        "caseRef": str(random_case['case_ref']),
        "productCode": "P_OR_H1",
        "channel": "PPO",
        "type": "FULFILMENT_CONFIRMED",
        "transactionId": str(uuid.uuid4())
    }

    message = {
        "type": "PUBSUB",
        "topic": Config.FULFILMENT_CONFIRMED_TOPIC_NAME,
        "project": Config.FULFILMENT_CONFIRMED_PROJECT,
        "delay": random_delay,
        "message_body": json.dumps(message_contents)
    }

    messages_to_send.append(message)


def prepare_undelivered_mail_reported(random_delay, random_case):
    message_contents = {
        "transactionId": str(uuid.uuid4()),
        "dateTime": f"{datetime.now().replace(microsecond=0).isoformat()}",
        "questionnaireId": random_case['qid'],
        "unreceipt": False
    }

    message = {
        "type": "PUBSUB",
        "topic": Config.QM_UNDELIVERED_TOPIC_NAME,
        "project": Config.QM_UNDELIVERED_PROJECT_ID,
        "delay": random_delay,
        "message_body": json.dumps(message_contents)
    }

    messages_to_send.append(message)


def prepare_address_modified(random_delay, random_case):
    message_contents = {
        "event": {
            "type": "ADDRESS_MODIFIED",
            "source": "CONTACT_CENTRE_API",
            "channel": "CC",
            "dateTime": f"{datetime.utcnow().isoformat()}Z",
            "transactionId": str(uuid.uuid4())
        },
        "payload": {
            "addressModification": {
                "collectionCase": {
                    "id": random_case['case_id']
                },
                "originalAddress": {
                    "addressLine1": "1 main street",
                    "addressLine2": "upper upperingham",
                    "addressLine3": "",
                    "townName": "upton",
                    "postcode": "UP103UP",
                    "region": "E",
                    "uprn": "123456789"
                },
                "newAddress": {
                    "addressLine1": "1a main street",
                    "addressLine2": "upper upperingham",
                    "addressLine3": "",
                    "townName": "upton",
                    "postcode": "UP103UP",
                    "region": "E",
                    "uprn": "123456789"
                }
            }
        }
    }

    message = {
        "type": "RABBIT",
        "topic": "event.case.address.update",
        "delay": random_delay,
        "message_body": json.dumps(message_contents)
    }

    messages_to_send.append(message)


def prepare_address_type_changed(random_delay, random_case):
    message_contents = {
        "event": {
            "type": "ADDRESS_TYPE_CHANGED",
            "source": "FIELDWORK_GATEWAY",
            "channel": "FIELD",
            "dateTime": f"{datetime.utcnow().isoformat()}Z",
            "transactionId": str(uuid.uuid4())
        },
        "payload": {
            "addressTypeChange": {
                "newCaseId": str(uuid.uuid4()),
                "collectionCase": {
                    "id": random_case['case_id'],
                    "ceExpectedCapacity": "20",
                    "address": {
                        "organisationName": "XXXXXXXXXXXXX",
                        "addressType": "CE",
                        "estabType": "XXX"
                    }
                }
            }
        }
    }

    message = {
        "type": "RABBIT",
        "topic": "event.case.address.update",
        "delay": random_delay,
        "message_body": json.dumps(message_contents)
    }

    messages_to_send.append(message)


def prepare_address_not_valid(random_delay, random_case):
    message_contents = {
        "event": {
            "type": "ADDRESS_NOT_VALID",
            "source": "FIELDWORK_GATEWAY",
            "channel": "FIELD",
            "dateTime": f"{datetime.utcnow().isoformat()}Z",
            "transactionId": str(uuid.uuid4())
        },
        "payload": {
            "invalidAddress": {
                "reason": "MERGED",
                "notes": "was 1a 1b and 1c",
                "collectionCase": {
                    "id": random_case['case_id']
                }
            }
        }
    }

    message = {
        "type": "RABBIT",
        "topic": "event.case.address.update",
        "delay": random_delay,
        "message_body": json.dumps(message_contents)
    }

    messages_to_send.append(message)


def prepare_new_address_reported(random_delay, random_case):
    message_contents = {
        "event": {
            "type": "NEW_ADDRESS_REPORTED",
            "source": "FIELDWORK_GATEWAY",
            "channel": "FIELD",
            "dateTime": f"{datetime.utcnow().isoformat()}Z",
            "transactionId": str(uuid.uuid4())
        },
        "payload": {
            "newAddress": {
                "sourceCaseId": random_case['case_id'],
                "collectionCase": {
                    "id": str(uuid.uuid4()),
                    "caseType": "SPG",
                    "survey": "CENSUS",
                    "fieldCoordinatorId": "SO_23",
                    "fieldOfficerId": "SO_23_123",
                    "address": {
                        "addressLine1": "100",
                        "addressLine2": "Kanes caravan park",
                        "addressLine3": "fairoak road",
                        "townName": "southampton",
                        "postcode": "SO190PG",
                        "region": "E",
                        "addressType": "SPG",
                        "addressLevel": "U",
                        "estabType": "Residential Caravaner",
                        "latitude": "50.917428",
                        "longitude": "-1.238193"
                    }
                }
            }
        }
    }

    message = {
        "type": "RABBIT",
        "topic": "event.case.address.update",
        "delay": random_delay,
        "message_body": json.dumps(message_contents)
    }

    messages_to_send.append(message)


def prepare_questionnaire_linked_message(random_delay, random_case, random_uac_qid):
    message_contents = {
        'event': {
            'type': 'QUESTIONNAIRE_LINKED',
            'source': 'FIELDWORK_GATEWAY',
            'channel': 'FIELD',
            "dateTime": "2011-08-12T20:17:46.384Z",
            "transactionId": "c45de4dc-3c3b-11e9-b210-d663bd873d93"
        },
        'payload': {
            'uac': {
                "caseId": random_case['case_id'],
                'questionnaireId': random_uac_qid['qid'],
            }
        }
    }

    message = {
        "type": "RABBIT",
        "topic": "event.questionnaire.update",
        "delay": random_delay,
        "message_body": json.dumps(message_contents)
    }

    messages_to_send.append(message)


def prepare_messages_to_be_sent():
    for _ in range(total_messages_to_send):
        random_message_type = message_type_randomiser[random.randint(0, len(message_type_randomiser) - 1)]
        random_delay = random.random() / message_rate  # In seconds
        random_case = test_cases[random.randint(0, len(test_cases) - 1)]
        random_uac_qid = test_unlinked_qids[random.randint(0, len(test_unlinked_qids) - 1)]

        if random_message_type == 'RESPONDENT_AUTHENTICATED':
            prepare_respondent_authenticated(random_delay, random_case)
        elif random_message_type == 'SURVEY_LAUNCHED':
            prepare_survey_launched(random_delay, random_case)
        elif random_message_type == 'RESPONSE_RECEIVED':
            prepare_response_received(random_delay, random_case)
        elif random_message_type == 'RESPONSE_RECEIVED.pqrs':
            prepare_response_received_pqrs(random_delay, random_case)
        elif random_message_type == 'RESPONSE_RECEIVED.qm':
            prepare_response_received_qm(random_delay, random_case)
        elif random_message_type == 'RESPONSE_RECEIVED.qm_blanks':
            prepare_response_received_qm_blanks(random_delay, random_case)
        elif random_message_type == 'REFUSAL_RECEIVED':
            prepare_refusal_received(random_delay, random_case)
        elif random_message_type == 'FULFILMENT_REQUESTED.sms':
            prepare_fulfilment_requested_sms(random_delay, random_case)
        elif random_message_type == 'FULFILMENT_REQUESTED.print':
            prepare_fulfilment_requested_print(random_delay, random_case)
        elif random_message_type == 'FULFILMENT_CONFIRMED':
            prepare_fulfilment_confirmed(random_delay, random_case)
        elif random_message_type == 'UNDELIVERED_MAIL_REPORTED':
            prepare_undelivered_mail_reported(random_delay, random_case)
        elif random_message_type == 'ADDRESS_MODIFIED':
            prepare_address_modified(random_delay, random_case)
        elif random_message_type == 'ADDRESS_TYPE_CHANGED':
            prepare_address_type_changed(random_delay, random_case)
        elif random_message_type == 'ADDRESS_NOT_VALID':
            prepare_address_not_valid(random_delay, random_case)
        elif random_message_type == 'NEW_ADDRESS_REPORTED':
            prepare_new_address_reported(random_delay, random_case)
        elif random_message_type == 'QUESTIONNAIRE_LINKED':
            prepare_questionnaire_linked_message(random_delay, random_case, random_uac_qid)



def send_rabbit_message(rabbit, message):
    rabbit.publish_message(message['message_body'], 'application/json', None, routing_key=message['topic'])


def send_pubsub_eq_receipt_message(publisher, message):
    topic_path = publisher.topic_path(message['project'], message['topic'])
    publisher.publish(topic_path,
                      data=message['message_body'].encode('utf-8'),
                      eventType='OBJECT_FINALIZE',
                      bucketId='eq-bucket',
                      objectId=message['tx_id'])


def send_pubsub_message(publisher, message):
    topic_path = publisher.topic_path(message['project'], message['topic'])
    publisher.publish(topic_path, data=message['message_body'].encode('utf-8'))


def send_the_messages():
    publisher = pubsub_v1.PublisherClient()

    with RabbitContext(exchange='events') as rabbit:
        for message in messages_to_send:
            time.sleep(message['delay'])

            if message['type'] == 'RABBIT':
                send_rabbit_message(rabbit, message)
            elif message['type'] == 'PUBSUB_EQ':
                send_pubsub_eq_receipt_message(publisher, message)
            elif message['type'] == 'PUBSUB':
                send_pubsub_message(publisher, message)


def main():
    prepare_randomiser()

    print("Preparing the data...")

    # Load a bunch of cases from the DB
    get_cases_from_db()
    get_unadressed_qids_from_db()

    # Prepare message to be sent, based on weightings etc
    prepare_messages_to_be_sent()

    # Send the Rabbit & Pubsub messages on separate threads
    print('Running load test...')
    send_the_messages()

    # Done!
    print('Finished load test.')


if __name__ == "__main__":
    main()
