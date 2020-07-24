import argparse
import json
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
    queue = queue
    message = json.dumps(
        {
            "message": "This is to spam",
        })
    with RabbitContext(exchange=Config.RABBITMQ_EXCHANGE) as rabbit:
        while datetime.utcnow() < end_time:
            rabbit.publish_message(
                message=message,
                content_type='application/json', headers='', routing_key='event.response.authentication')


def main():
    args = parse_arguments()
    spam(args.queue, args.duration)


if __name__ == "__main__":
    main()
