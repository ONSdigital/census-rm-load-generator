import concurrent
import json
import random
import time
import uuid
from datetime import datetime

from google.cloud import pubsub_v1

from config import Config
from utilities.db_helper import execute_sql_query
from utilities.pub import SuperBunny
from utilities.rabbit_context import RabbitContext

message_rate = int(Config.MESSAGE_RATE)  # Per second
message_settings = {
    "RESPONDENT_AUTHENTICATED": {"weight": 35, "chaos": 0.001},
    "SURVEY_LAUNCHED": {"weight": 33, "chaos": 0.001},
    "RESPONSE_RECEIVED": {"weight": 16, "chaos": 0.001},
    "RESPONSE_RECEIVED.pqrs": {"weight": 1, "chaos": 0.001},
    "RESPONSE_RECEIVED.qm": {"weight": 1, "chaos": 0.001},
    "RESPONSE_RECEIVED.qm_blanks": {"weight": 1, "chaos": 0.001},
    "REFUSAL_RECEIVED": {"weight": 1, "chaos": 0.001},
    "FULFILMENT_REQUESTED.sms": {"weight": 1, "chaos": 0.001},
    "FULFILMENT_REQUESTED.print": {"weight": 1, "chaos": 0.001},
    "FULFILMENT_REQUESTED.EQ.sms": {"weight": 1, "chaos": 0.001},
    "FULFILMENT_REQUESTED.EQ.print": {"weight": 1, "chaos": 0.001},
    "UNDELIVERED_MAIL_REPORTED": {"weight": 1, "chaos": 0.001},
    "FULFILMENT_CONFIRMED": {"weight": 1, "chaos": 0.001},
    "NEW_ADDRESS_REPORTED": {"weight": 1, "chaos": 0.001},
    "ADDRESS_NOT_VALID": {"weight": 1, "chaos": 0.001},
    "ADDRESS_TYPE_CHANGED": {"weight": 1, "chaos": 0.001},
    "ADDRESS_MODIFIED": {"weight": 1, "chaos": 0.001},
    "PRINT_CASE_SELECTED": {"weight": 1, "chaos": 0.001},
    "QUESTIONNAIRE_LINKED": {"weight": 1, "chaos": 0.001}
}
message_type_randomiser = []

test_cases = []
test_unlinked_qids = []

total_messages_to_send = int(Config.TOTAL_MESSAGES_TO_SEND)
messages_to_send = []


def prepare_randomiser():
    for key, value in message_settings.items():
        for _ in range(value['weight']):
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


def get_chaotic_qid(qid, random_chaos, one_in_n):
    if random_chaos and random.randint(1, one_in_n) == 1:
        return str(random.randint(100000000000, 999999999999))
    else:
        return qid


def get_chaotic_case_id(case_id, random_chaos, one_in_n):
    if random_chaos and random.randint(1, one_in_n) == 1:
        return str(uuid.uuid4())
    else:
        return case_id


def get_chaotic_phone_number(phone_number, random_chaos, one_in_n):
    if random_chaos and random.randint(1, one_in_n) == 1:
        return str(random.randint(100000, 999999))
    else:
        return phone_number


def get_chaotic_case_ref(case_ref, random_chaos, one_in_n):
    if random_chaos and random.randint(1, one_in_n) == 1:
        return str(random.randint(100000000000, 999999999999))
    else:
        return case_ref


def prepare_respondent_authenticated(random_delay, random_case, random_chaos):
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
                "questionnaireId": get_chaotic_qid(random_case['qid'], random_chaos, 2),
                "caseId": get_chaotic_case_id(random_case['case_id'], random_chaos, 2)
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


def prepare_survey_launched(random_delay, random_case, random_chaos):
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
                "questionnaireId": get_chaotic_qid(random_case['qid'], random_chaos, 2),
                "caseId": get_chaotic_case_id(random_case['case_id'], random_chaos, 2),
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


def prepare_response_received(random_delay, random_case, random_chaos):
    tx_id = str(uuid.uuid4())

    message_contents = {
        "timeCreated": f"{datetime.utcnow().isoformat()}Z",
        "metadata": {
            "case_id": get_chaotic_case_id(random_case['case_id'], random_chaos, 2),
            "tx_id": tx_id,
            "questionnaire_id": get_chaotic_qid(random_case['qid'], random_chaos, 2),
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


def prepare_response_received_pqrs(random_delay, random_case, random_chaos):
    prepare_response_received_pqrs_and_qm(random_delay, random_case, "PQRS", random_chaos)


def prepare_response_received_qm(random_delay, random_case, random_chaos):
    prepare_response_received_pqrs_and_qm(random_delay, random_case, "QM", random_chaos)


def prepare_response_received_pqrs_and_qm(random_delay, random_case, channel, random_chaos):
    tx_id = str(uuid.uuid4())

    message_contents = {
        "channel": channel,
        "dateTime": f"{datetime.utcnow().isoformat()}Z",
        "questionnaireId": get_chaotic_qid(random_case['qid'], random_chaos, 1),
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


def prepare_response_received_qm_blanks(random_delay, random_case, random_chaos):
    tx_id = str(uuid.uuid4())

    message_contents = {
        "channel": "QM",
        "dateTime": f"{datetime.utcnow().isoformat()}Z",
        "questionnaireId": get_chaotic_qid(random_case['qid'], random_chaos, 1),
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


def prepare_refusal_received(random_delay, random_case, random_chaos):
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
                    "id": get_chaotic_case_id(random_case['case_id'], random_chaos, 1)
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


def prepare_fulfilment_requested_sms(random_delay, random_case, random_chaos):
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
                "caseId": get_chaotic_case_id(random_case['case_id'], random_chaos, 2),
                "address": {},
                "contact": {
                    "telNo": get_chaotic_phone_number("+447876224123", random_chaos, 2)
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


def prepare_fulfilment_requested_print(random_delay, random_case, random_chaos):
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
                "caseId": get_chaotic_case_id(random_case['case_id'], random_chaos, 1),
                "address": {},
                "contact": {}
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


def prepare_fulfilment_confirmed(random_delay, random_case, random_chaos):
    message_contents = {
        "dateTime": f"{datetime.utcnow().isoformat()}Z",
        "caseRef": get_chaotic_case_ref(str(random_case['case_ref']), random_chaos, 1),
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


def prepare_undelivered_mail_reported(random_delay, random_case, random_chaos):
    message_contents = {
        "transactionId": str(uuid.uuid4()),
        "dateTime": f"{datetime.now().replace(microsecond=0).isoformat()}",
        "questionnaireId": get_chaotic_qid(random_case['qid'], random_chaos, 1),
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


def prepare_address_modified(random_delay, random_case, random_chaos):
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
                    "id": get_chaotic_case_id(random_case['case_id'], random_chaos, 1)
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


def prepare_address_type_changed(random_delay, random_case, random_chaos):
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
                    "id": get_chaotic_case_id(random_case['case_id'], random_chaos, 1),
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


def prepare_address_not_valid(random_delay, random_case, random_chaos):
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
                    "id": get_chaotic_case_id(random_case['case_id'], random_chaos, 1)
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


def prepare_new_address_reported(random_delay, random_case, random_chaos):
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
                "sourceCaseId": get_chaotic_case_id(random_case['case_id'], random_chaos, 1),
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


def prepare_questionnaire_linked_message(random_delay, random_case, random_uac_qid, random_chaos):
    message_contents = {
        'event': {
            'type': 'QUESTIONNAIRE_LINKED',
            'source': 'FIELDWORK_GATEWAY',
            'channel': 'FIELD',
            "dateTime": f"{datetime.utcnow().isoformat()}Z",
            "transactionId": str(uuid.uuid4())
        },
        'payload': {
            'uac': {
                "caseId": get_chaotic_case_id(random_case['case_id'], random_chaos, 2),
                'questionnaireId': get_chaotic_qid(random_uac_qid['qid'], random_chaos, 2),
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


def prepare_eq_sms_fulfilment_request(random_delay, random_case, random_chaos):
    message_contents = {
        "event": {
            "type": "FULFILMENT_REQUESTED",
            "source": "QUESTIONNAIRE_RUNNER",
            "channel": "EQ",
            "dateTime": f"{datetime.utcnow().isoformat()}Z",
            "transactionId": str(uuid.uuid4())
        },
        "payload": {
            "fulfilmentRequest": {
                "fulfilmentCode": "UACIT1",
                "caseId": get_chaotic_case_id(random_case['case_id'], random_chaos, 2),
                "individualCaseId": str(uuid.uuid4()),
                "contact": {
                    "telNo": get_chaotic_phone_number("+447876224123", random_chaos, 2)
                }
            }
        }
    }

    message = {
        "type": "PUBSUB",
        "topic": Config.EQ_FULFILMENT_TOPIC_NAME,
        "project": Config.EQ_FULFILMENT_PROJECT_NAME,
        "delay": random_delay,
        "message_body": json.dumps(message_contents)
    }

    messages_to_send.append(message)


def prepare_eq_print_fulfilment_request(random_delay, random_case, random_chaos):
    message_contents = {
        "event": {
            "type": "FULFILMENT_REQUESTED",
            "source": "QUESTIONNAIRE_RUNNER",
            "channel": "EQ",
            "dateTime": f"{datetime.utcnow().isoformat()}Z",
            "transactionId": str(uuid.uuid4())
        },
        "payload": {
            "fulfilmentRequest": {
                "fulfilmentCode": "P_UAC_UACIP1",
                "caseId": get_chaotic_case_id(random_case['case_id'], random_chaos, 1),
                "individualCaseId": str(uuid.uuid4()),
                "contact": {}
            }
        }
    }

    message = {
        "type": "PUBSUB",
        "topic": Config.EQ_FULFILMENT_TOPIC_NAME,
        "project": Config.EQ_FULFILMENT_PROJECT_NAME,
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
        random_chaos = random.random() < message_settings[random_message_type]['chaos']

        if random_message_type == 'RESPONDENT_AUTHENTICATED':
            prepare_respondent_authenticated(random_delay, random_case, random_chaos)
        elif random_message_type == 'SURVEY_LAUNCHED':
            prepare_survey_launched(random_delay, random_case, random_chaos)
        elif random_message_type == 'RESPONSE_RECEIVED':
            prepare_response_received(random_delay, random_case, random_chaos)
        elif random_message_type == 'RESPONSE_RECEIVED.pqrs':
            prepare_response_received_pqrs(random_delay, random_case, random_chaos)
        elif random_message_type == 'RESPONSE_RECEIVED.qm':
            prepare_response_received_qm(random_delay, random_case, random_chaos)
        elif random_message_type == 'RESPONSE_RECEIVED.qm_blanks':
            prepare_response_received_qm_blanks(random_delay, random_case, random_chaos)
        elif random_message_type == 'REFUSAL_RECEIVED':
            prepare_refusal_received(random_delay, random_case, random_chaos)
        elif random_message_type == 'FULFILMENT_REQUESTED.sms':
            prepare_fulfilment_requested_sms(random_delay, random_case, random_chaos)
        elif random_message_type == 'FULFILMENT_REQUESTED.print':
            prepare_fulfilment_requested_print(random_delay, random_case, random_chaos)
        elif random_message_type == 'FULFILMENT_CONFIRMED':
            prepare_fulfilment_confirmed(random_delay, random_case, random_chaos)
        elif random_message_type == 'UNDELIVERED_MAIL_REPORTED':
            prepare_undelivered_mail_reported(random_delay, random_case, random_chaos)
        elif random_message_type == 'ADDRESS_MODIFIED':
            prepare_address_modified(random_delay, random_case, random_chaos)
        elif random_message_type == 'ADDRESS_TYPE_CHANGED':
            prepare_address_type_changed(random_delay, random_case, random_chaos)
        elif random_message_type == 'ADDRESS_NOT_VALID':
            prepare_address_not_valid(random_delay, random_case, random_chaos)
        elif random_message_type == 'NEW_ADDRESS_REPORTED':
            prepare_new_address_reported(random_delay, random_case, random_chaos)
        elif random_message_type == 'QUESTIONNAIRE_LINKED':
            prepare_questionnaire_linked_message(random_delay, random_case, random_uac_qid, random_chaos)
        elif random_message_type == 'FULFILMENT_REQUEST.EQ.sms':
            prepare_eq_sms_fulfilment_request(random_delay, random_case, random_chaos)
        elif random_message_type == 'FULFILMENT_REQUEST.EQ.print':
            prepare_eq_print_fulfilment_request(random_delay, random_case, random_chaos)


def send_rabbit_message(rabbit, message):
    print('About to send cuntting msg')
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

    with SuperBunny(exchange='events') as rabbit:
        time.sleep(5)
        for message in messages_to_send:
            # time.sleep(message['delay'])

            if message['type'] == 'RABBIT':
                send_rabbit_message(rabbit, message)
            elif message['type'] == 'PUBSUB_EQ':
                send_pubsub_eq_receipt_message(publisher, message)
            elif message['type'] == 'PUBSUB':
                send_pubsub_message(publisher, message)

#     msg_chunks = split_msgs(messages_to_send)
#
#     with concurrent.futures.ThreadPoolExecutor() as executor:
#         futures = []
#
#         for msgs in msg_chunks:
#             futures.append(executor.submit(send_msgs, msgs=msgs, info='proc'))
#
#         for future in concurrent.futures.as_completed(futures):
#             print(future.result())
#
#
# def split_msgs(msgs):
#     size = len(msgs) // 4
#
#     for i in range(0, len(msgs), size):
#         yield msgs[i:i + size]
#
#
# def send_msgs(msgs=None, info='blah'):
#     publisher = pubsub_v1.PublisherClient()
#     print('Running ', info)
#
#     with RabbitContext(exchange='events') as rabbit:
#         for message in msgs:
#             # time.sleep(message['delay'])
#
#             if message['type'] == 'RABBIT':
#                 send_rabbit_message(rabbit, message)
#             elif message['type'] == 'PUBSUB_EQ':
#                 send_pubsub_eq_receipt_message(publisher, message)
#             elif message['type'] == 'PUBSUB':
#                 send_pubsub_message(publisher, message)
#
#     print('Finished ', info)


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
