import threading
import time
import paho.mqtt.client as mqtt_client
import random

STAT_DISCONNECTED = 'disconnected'
STAT_CONNECTING = 'disconnected'
STAT_CONNECTED = 'connected'
STAT_SUBSCRIBED = 'subscribed'

class MqttCli:
    def __init__(self, host, port, username, passwd, topics, cb_on_message=None):
        self.host = host
        self.port = port
        self.username = username
        self.passwd = passwd
        self.stat = STAT_DISCONNECTED

        client_id = f'ucl-alg-{random.randint(0, 100000)}'
        self.client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1, client_id)
        self.client.username_pw_set(self.username, self.passwd)

        self.topics = topics
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
            self.stat = STAT_CONNECTED
            # 订阅主题列表
            self.subscribe()
        else:
            print(f"Failed to connect, return code {rc}")
            self.stat = STAT_DISCONNECTED

    def on_message(self, client, userdata, message):
        print(f"Received `{message.payload.decode()}` from `{message.topic}` topic")
        # if self.cb_on_message:
        #     self.cb_on_message(message.topic, message.payload.decode())

    def connect(self):
        self.stat = STAT_CONNECTING
        # set the client to be alive indefinitely
        self.client.connect(host=self.host, port=self.port, keepalive=0)
        # todo: check the loop function to see if it is blocking
        self.client.loop_start()
        # self.client.loop()
        return 0

    def disconnect(self):
        self.stat = STAT_DISCONNECTED
        self.client.disconnect()
        self.client.loop_stop(force=True)

    def subscribe(self):
        # 订阅单个主题或者多个主题
        if isinstance(self.topics, str):
            self.client.subscribe(self.topics)
        elif isinstance(self.topics, list):
            for topic in self.topics:
                self.client.subscribe(topic)
        else:
            print("Invalid topics format. Should be a string or a list of strings.")

    def publish(self, message):
        """publish to default topics[0]"""
        self.client.publish(self.topics, message)
        print(f"Send `{message}` to topic `{self.topics}`")

    def publish_to(self, topic, message):
        """specify topic to publish"""
        self.client.publish(topic, message)
        print(f"Send `{message}` to topic `{topic}`")
