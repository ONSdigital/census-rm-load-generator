import json
import random
import time
import uuid
from datetime import datetime

from google.cloud import pubsub_v1

from config import Config
from utilities.db_helper import execute_sql_query
from utilities.rabbit_context import RabbitContext

message_rate = 1000  # Per second
message_weightings = {
    "RESPONDENT_AUTHENTICATED": 37,
    "SURVEY_LAUNCHED": 35,
    "RESPONSE_RECEIVED": 20,
    "REFUSAL_RECEIVED": 5,
    "FULFILMENT_REQUESTED": 2,
    "UNDELIVERED_MAIL_REPORTED": 1
}
message_type_randomiser = []

test_cases = []

total_messages_to_send = 10000
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


def prepare_fulfilment_requested(random_delay, random_case):
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


def prepare_messages_to_be_sent():
    for _ in range(total_messages_to_send):
        random_message_type = message_type_randomiser[random.randint(0, len(message_type_randomiser) - 1)]
        random_delay = float(random.randint(0, 1000 / message_rate)) / 1000.0
        random_case = test_cases[random.randint(0, len(test_cases) - 1)]

        if random_message_type == 'RESPONDENT_AUTHENTICATED':
            prepare_respondent_authenticated(random_delay, random_case)
        elif random_message_type == 'SURVEY_LAUNCHED':
            prepare_survey_launched(random_delay, random_case)
        elif random_message_type == 'RESPONSE_RECEIVED':
            prepare_response_received(random_delay, random_case)
        elif random_message_type == 'REFUSAL_RECEIVED':
            prepare_refusal_received(random_delay, random_case)
        elif random_message_type == 'FULFILMENT_REQUESTED':
            prepare_fulfilment_requested(random_delay, random_case)
        elif random_message_type == 'UNDELIVERED_MAIL_REPORTED':
            prepare_undelivered_mail_reported(random_delay, random_case)


def send_rabbit_message(rabbit, message):
    rabbit.publish_message(message['message_body'], 'application/json', None, routing_key=message['topic'])


def send_pubsub_eq_receipt_message(publisher, message):
    topic_path = publisher.topic_path(message['project'], message['topic'])
    future = publisher.publish(topic_path,
                               data=message['message_body'].encode('utf-8'),
                               eventType='OBJECT_FINALIZE',
                               bucketId='eq-bucket',
                               objectId=message['tx_id'])
    future.add_done_callback(pubsub_message_callback)


def send_pubsub_message(publisher, message):
    topic_path = publisher.topic_path(message['project'], message['topic'])
    future = publisher.publish(topic_path, data=message['message_body'].encode('utf-8'))
    future.add_done_callback(pubsub_message_callback)


def pubsub_message_callback(result):
    pass


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
    print('Running load test...')

    prepare_randomiser()

    # Load a bunch of cases from the DB
    get_cases_from_db()

    # Prepare message to be sent, based on weightings etc
    prepare_messages_to_be_sent()

    # Send the Rabbit & Pubsub messages on separate threads
    send_the_messages()

    # Done!
    print('Finished load test.')


if __name__ == "__main__":
    main()
