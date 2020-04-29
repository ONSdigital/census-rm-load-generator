import os


class Config:
    RABBITMQ_HOST = os.getenv('RABBITMQ_SERVICE_HOST', 'localhost')
    RABBITMQ_PORT = os.getenv('RABBITMQ_SERVICE_PORT', '6672')
    RABBITMQ_HTTP_PORT = os.getenv('RABBITMQ_HTTP_PORT', '16672')
    RABBITMQ_VHOST = os.getenv('RABBITMQ_VHOST', '/')
    RABBITMQ_EXCHANGE = os.getenv('RABBITMQ_EXCHANGE', '')
    RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'guest')
    RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD', 'guest')
    DB_USERNAME = os.getenv('DB_USERNAME', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '6432')
    DB_NAME = os.getenv('DB_NAME', 'postgres')
    DB_USESSL = os.getenv('DB_USESSL', '')
    RECEIPT_TOPIC_ID = os.getenv('RECEIPT_TOPIC_ID', 'eq-submission-topic')
    RECEIPT_TOPIC_PROJECT = os.getenv('RECEIPT_TOPIC_PROJECT', 'project')
    QM_UNDELIVERED_TOPIC_NAME = "qm-undelivered-topic"
    QM_UNDELIVERED_PROJECT_ID = os.getenv("QM_UNDELIVERED_PROJECT_ID",
                                          "qm-undelivered-project")
    CASES_TO_FETCH = os.getenv("CASES_TO_FETCH", "50")
