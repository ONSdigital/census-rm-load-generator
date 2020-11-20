import json
import uuid
from datetime import datetime

import pika

# Step #3
from config import Config


def on_open(connection):
    print('Opened Connection')
    connection.channel(on_open_callback=on_channel_open)


# Step #4
def on_channel_open(channel):
    print('On channel open, stick big ffing loop here')

    message = json.dumps({
        "event": {
            "type": "SURVEY_LAUNCHED",
            "source": "CONTACT_CENTRE_API",
            "channel": "CC",
            "dateTime": f"{datetime.utcnow().isoformat()}Z",
            "transactionId": str(uuid.uuid4())
        },
        "payload": {
            "response": {
                "questionnaireId": '034343434r34',
                "caseId": str(uuid.uuid4()),
                "agentId": "cc_000351"
            }
        }
    })

    # message = json.dumps(
    #     {
    #         "message": "This is to spam",
    #     })

    x = range(0, 100000)

    # event.response.receipt
    # 'event.response.authentication'

    routing_keys = ['event.case.*', 'event.case.address.update', 'event.case.update', 'event.case.update',
                    'event.ccs.propertylisting',
                    'event.fieldcase.update', 'event.fulfilment.confirmation', 'event.fulfilment.request',
                    'event.fulfilment.request',
                    'event.fulfilment.request', 'event.fulfilment.undelivered', 'event.questionnaire.update',
                    'event.respondent.refusal', 'event.response.authentication', 'event.response.receipt',
                    'event.uac.*',
                    'event.uac.update']

    for _ in x:
        for k in routing_keys:
            channel.basic_publish('events',
                                  k,
                                  message,
                                  pika.BasicProperties(content_type='text/plain',
                                                       delivery_mode=1))


    # connection.close()
    # print('Finished publishing')


def main():
    parameters = pika.ConnectionParameters(Config.RABBITMQ_HOST,
                                           Config.RABBITMQ_PORT,
                                           Config.RABBITMQ_VHOST,
                                           pika.PlainCredentials(Config.RABBITMQ_USER, Config.RABBITMQ_PASSWORD))

    # parameters = pika.URLParameters('amqp://guest:guest@localhost:5672/%2F')

    connection = pika.SelectConnection(parameters=parameters,
                                       on_open_callback=on_open)

    try:

        # Step #2 - Block on the IOLoop
        connection.ioloop.start()

    # Catch a Keyboard Interrupt to make sure that the connection is closed cleanly
    except KeyboardInterrupt:

        # Gracefully close the connection
        connection.close()

        # Start the IOLoop again so Pika can communicate, it will stop on its own when the connection is closed
        connection.ioloop.start()


if __name__ == "__main__":
    main()

# Step #1: C
# onnect to RabbitMQ
