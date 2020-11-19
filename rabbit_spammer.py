import argparse
import json
import uuid
from datetime import datetime, timedelta

from config import Config
from utilities.rabbit_context import RabbitContext


def parse_arguments():
    parser = argparse.ArgumentParser(description='Time duration')
    parser.add_argument('queue', help='queue', type=str)
    parser.add_argument('duration', help='time to run for in minutes', type=int)
    return parser.parse_args()


def spam(queue, duration):
    end_time = datetime.utcnow() + timedelta(0, 0, 0, 0, float(duration))
    # message = json.dumps(
    #     {
    #         "message": "This is to spam",
    #     })

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
                "caseId":  str(uuid.uuid4()),
                "agentId": "cc_000351"
            }
        }
    })

    with RabbitContext(exchange='events') as rabbit:
        while datetime.utcnow() < end_time:
            rabbit.publish_message(
                message=message,
                content_type='application/json', headers='', routing_key='event.response.authentication')


def main():
    # args = parse_arguments()
    # spam(args.queue, args.duration)
    # spam('event.response.authentication', 100)
    spam('event.response.receipt', 100)


if __name__ == "__main__":
    main()
