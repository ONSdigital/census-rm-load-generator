import pika
from pika.spec import PERSISTENT_DELIVERY_MODE

from config import Config
from utilities.exceptions import RabbitConnectionClosedError


class RabbitContext:

    def __init__(self, **kwargs):
        self._host = kwargs.get('host') or Config.RABBITMQ_HOST
        self._port = kwargs.get('port') or Config.RABBITMQ_PORT
        self._vhost = kwargs.get('vhost') or Config.RABBITMQ_VHOST
        self._exchange = kwargs.get('exchange') or Config.RABBITMQ_EXCHANGE
        self._user = kwargs.get('user') or Config.RABBITMQ_USER
        self._password = kwargs.get('password') or Config.RABBITMQ_PASSWORD
        self.queue_name = kwargs.get('queue_name')
        self.queue_declare_result = None

    def __enter__(self):
        self.open_connection()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_connection()

    @property
    def channel(self):
        return self._channel

    def open_connection(self):
        self._connection = pika.BlockingConnection(
            pika.ConnectionParameters(self._host,
                                      self._port,
                                      self._vhost,
                                      pika.PlainCredentials(self._user, self._password)))

        self._channel = self._connection.channel()

        # Limit to 100 messages to avoid rabbit 'issues'
        self._channel.basic_qos(prefetch_count=100)

        if self.queue_name:
            self.queue_declare_result = self._channel.queue_declare(queue=self.queue_name, durable=True)

        return self._connection

    def close_connection(self):
        self._connection.close()
        del self._channel
        del self._connection

    def publish_message(self, message: str, content_type: str, headers, exchange=None, routing_key=None):
        if not self._connection.is_open:
            raise RabbitConnectionClosedError

        self.channel.basic_publish(
            exchange=exchange or self._exchange,
            routing_key=routing_key or self.queue_name,
            body=message,
            properties=pika.BasicProperties(content_type=content_type, headers=headers,
                                            delivery_mode=PERSISTENT_DELIVERY_MODE))

    def get_queue_message_qty(self):
        return self.queue_declare_result.method.message_count

    def start_listening_for_messages(self, on_message_callback, timeout=30):
        self._connection.call_later(
            delay=timeout,
            callback=self._timeout_callback)

        self.channel.basic_consume(
            queue=self.queue_name,
            on_message_callback=on_message_callback)
        self.channel.start_consuming()

    def _timeout_callback(self):
        self.channel.stop_consuming()
