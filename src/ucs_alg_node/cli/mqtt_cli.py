import threading
import time

import paho.mqtt.client as mqtt

import json

STAT_DISCONNECTED = 'disconnected'
STAT_CONNECTING = 'connecting'
STAT_CONNECTED = 'connected'

class MqttCli:
    """
    MQTT Cli wrapper
    N.B.: any MQ may bet lost, if the algorithm is in batch mode, preferably pass the result to
    a database or a file
    """

    def __init__(self, host, port, username, passwd, topics, id=None, on_connect=None, on_message=None, on_publish=None, on_subscribe=None, on_disconnect=None):
        self.host = host
        self.port = port
        self.username = username
        self.passwd = passwd
        self.stat = STAT_DISCONNECTED

        self.cli_id = id # the id should be the node's id
        self.cli = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.cli.id = self.cli_id
        self.cli.username_pw_set(self.username, self.passwd)
        self.topics = topics
        self.on_connect = on_connect
        self.on_message = on_message
        self.on_publish = on_publish
        self.on_subscribe = on_subscribe
        self.on_disconnect = on_disconnect

        # register callbacks
        def on_connect(client, userdata, flags, rc, properties):
            # print('connected', rc)
            self.stat = STAT_CONNECTED

            if rc == 'Success':
                print('connected')
                for topic in topics:
                    self.cli.subscribe(topic)

                if self.on_connect:
                    self.on_connect()

            else:
                self.stat = STAT_DISCONNECTED
                self.disconnect()


        def on_disconnect(client, userdata, rc):
            self.stat = STAT_DISCONNECTED
            time.sleep(0.01)
            # auto-reconnect
            self.connect()

        def on_subscribe(client, userdata, mid, granted_qos, properties):
            print('subscribed')

        def on_publish(client, userdata, mid, rc, properties):
            print('cli published')

        def on_message(client, userdata, message):
            if self.on_message:
                self.on_message(message.topic, message.payload)
            # print('received: ', message.payload)

        self.cli.on_connect = on_connect
        self.cli.on_publish = on_publish
        self.cli.on_subscribe = on_subscribe
        self.cli.on_disconnect = on_disconnect
        self.on_message = on_message

    def connect(self):
        self.stat = STAT_CONNECTING
        # set the client to be alive indefinitely
        self.cli.connect(host=self.host, port=self.port, keepalive=60, )

    def disconnect(self):
        self.stat = STAT_DISCONNECTED
        self.cli.disconnect()

    def subscribe(self, topic):
        self.cli.subscribe(topic)

    def publish(self, topic=None, message=None):
        """publish to default topics[0]"""
        if not topic:
            self.cli.publish(self.topics[0], message)
        else:
            self.cli.publish(topic, json.dumps(message))