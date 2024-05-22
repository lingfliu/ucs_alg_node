import threading
import time

import paho.mqtt.client as mqtt_client
import random

STAT_DISCONNECTED = 'disconnected'
STAT_CONNECTING = 'disconnected'
STAT_CONNECTED = 'connected'
STAT_SUBSCRIBED = 'subscribed'


class MqttCli:
    """N.B.: any MQ may bet lost, if the algorithm is in batch mode, should pass the result to
    a database or a file
    """
    def __init__(self, host, port, username, passwd, topics, cb_on_message=None):
        self.host = host
        self.port = port
        self.username = username
        self.passwd = passwd
        self.stat = STAT_DISCONNECTED

        client_id = f'ucl-alg-{random.randint(0, 100000)}'
        self.client = mqtt_client.Client(client_id)
        self.client.username_pw_set(self.username, self.passwd)

        self.topics = topics

        # register callbacks
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
                self.stat = STAT_CONNECTED
            else:
                print("Failed to connect, return code %d\n", rc)
                self.stat = STAT_DISCONNECTED
            for topic in topics:
                self.client.subscribe(topic)
        self.client.on_connect = on_connect

        def on_disconnect(client, userdata, rc):
            print("Disconnected from MQTT Broker!")
            self.stat = STAT_DISCONNECTED
            time.sleep(0.01)
            # auto-reconnect
            self.connect()

        self.client.on_disconnect = on_disconnect

        def on_publish():
            pass
        self.client.on_publish = on_publish

        self.cb_on_message = cb_on_message

        def on_message(client, userdata, message):
            # print(f"Received `{message.payload.decode()}` from `{message.topic}` topic")
            if self.cb_on_message:
                self.cb_on_message(message.topic, message.payload.decode())

        self.client.on_message = on_message

    def connect(self):
        self.stat = STAT_CONNECTING
        # set the client to be alive indefinitely
        self.client.connect(host=self.host, port=self.port, keepalive=0)
        # todo: check the loop function to see if it is blocking
        self.client.loop_start()
        self.client.loop()
        return 0

    def disconnect(self):
        self.stat = STAT_DISCONNECTED
        self.client.disconnect()
        self.client.loop_stop(force=True)

    def subscribe(self, topic):
        self.client.subscribe(topic)

    def publish(self, message):
        """publish to default topics[0]"""
        self.client.publish(self.topics[0], message)

    def publish_to(self, topic, message):
        """specify topic to publish"""
        self.client.publish(topic, message)