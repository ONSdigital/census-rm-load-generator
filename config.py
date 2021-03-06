import os


class Config:
    RABBITMQ_HOST = os.getenv('RABBIT_HOST', 'localhost')
    RABBITMQ_PORT = os.getenv('RABBIT_PORT', '6672')
    RABBITMQ_VHOST = os.getenv('RABBITMQ_VHOST', '/')
    RABBITMQ_EXCHANGE = os.getenv('RABBITMQ_EXCHANGE', '')
    RABBITMQ_USER = os.getenv('RABBIT_USERNAME', 'guest')
    RABBITMQ_PASSWORD = os.getenv('RABBIT_PASSWORD', 'guest')
    DB_USERNAME = os.getenv('DB_USERNAME', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '6432')
    DB_NAME = os.getenv('DB_NAME', 'postgres')
    DB_USESSL = os.getenv('DB_USESSL', '')
    RECEIPT_TOPIC_ID = os.getenv('RECEIPT_TOPIC_ID', 'eq-submission-topic')
    RECEIPT_TOPIC_PROJECT = os.getenv('RECEIPT_TOPIC_PROJECT', 'project')
    OFFLINE_RECEIPT_TOPIC_PROJECT_ID = os.getenv('OFFLINE_RECEIPT_TOPIC_PROJECT_ID', 'offline-project')
    OFFLINE_RECEIPT_TOPIC_NAME = os.getenv('OFFLINE_RECEIPT_TOPIC_NAME', 'offline-receipt-topic')
    QM_UNDELIVERED_TOPIC_NAME = "qm-undelivered-topic"
    QM_UNDELIVERED_PROJECT_ID = os.getenv("QM_UNDELIVERED_PROJECT_ID",
                                          "qm-undelivered-project")
    FULFILMENT_CONFIRMED_TOPIC_NAME = "fulfilment-confirmed-topic"
    FULFILMENT_CONFIRMED_PROJECT = os.getenv('FULFILMENT_CONFIRMED_PROJECT', 'fulfilment-confirmed-project')
    EQ_FULFILMENT_TOPIC_NAME = "eq-fulfilment-topic"
    EQ_FULFILMENT_PROJECT_NAME = os.getenv('FULFILMENT_CONFIRMED_PROJECT', 'eq-fulfilment-project')
    CASES_TO_FETCH = os.getenv("CASES_TO_FETCH", "1000000")
    OFFSET_FOR_CASES = os.getenv("OFFSET_FOR_CASES", 0)  # Used to Select case range via Offset
    UNADDRESSED_QIDS_TO_FETCH = os.getenv("UNADDRESSED_QIDS_TO_FETCH", "100000")
    OFFSET_FOR_UNADDRESSED_QIDS = os.getenv("OFFSET_FOR_UNADDRESSED_QIDS", 0)  # Used to Select qids range via Offset
    MESSAGE_RATE_THROTTLE = os.getenv("MESSAGE_RATE_THROTTLE", False)  # This publishes with no delay
    MESSAGE_RATE = os.getenv("MESSAGE_RATE", "10000")  # Messages per second, is MESSAGE_RATE_THROTTLE enabled
    TOTAL_MESSAGES_TO_SEND = os.getenv("TOTAL_MESSAGES_TO_SEND", "1000000")
    CHAOS = os.getenv('CHAOS', 0)
    API_CALL_RATE = os.getenv("API_CALL_RATE", "1000")  # Calls per second
    TOTAL_API_CALLS = os.getenv("TOTAL_API_CALLS", "10000")
    CASE_API_URL = os.getenv("CASE_API_URL", "http://case-api:80")

    MESSAGE_SETTINGS = {
        "RESPONDENT_AUTHENTICATED": {"weight": 35, "chaos": CHAOS},
        "SURVEY_LAUNCHED": {"weight": 35, "chaos": CHAOS},
        "RESPONSE_RECEIVED": {"weight": 16, "chaos": CHAOS},
        "RESPONSE_RECEIVED.pqrs": {"weight": 1, "chaos": CHAOS},
        "RESPONSE_RECEIVED.qm": {"weight": 1, "chaos": CHAOS},
        "RESPONSE_RECEIVED.qm_blanks": {"weight": 1, "chaos": CHAOS},
        "REFUSAL_RECEIVED": {"weight": 1, "chaos": CHAOS},
        "FULFILMENT_REQUESTED.sms": {"weight": 1, "chaos": CHAOS},
        "FULFILMENT_REQUESTED.print": {"weight": 1, "chaos": CHAOS},
        "FULFILMENT_REQUESTED.EQ.sms": {"weight": 1, "chaos": CHAOS},
        "FULFILMENT_REQUESTED.EQ.print": {"weight": 1, "chaos": CHAOS},
        "UNDELIVERED_MAIL_REPORTED": {"weight": 1, "chaos": CHAOS},
        "FULFILMENT_CONFIRMED": {"weight": 1, "chaos": CHAOS},
        "NEW_ADDRESS_REPORTED": {"weight": 1, "chaos": CHAOS},
        "ADDRESS_NOT_VALID": {"weight": 1, "chaos": CHAOS},
        "ADDRESS_TYPE_CHANGED": {"weight": 1, "chaos": CHAOS},
        "ADDRESS_MODIFIED": {"weight": 1, "chaos": CHAOS},
        "PRINT_CASE_SELECTED": {"weight": 1, "chaos": CHAOS},
        "QUESTIONNAIRE_LINKED": {"weight": 1, "chaos": CHAOS}
    }
