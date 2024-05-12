import paho.mqtt.client as mqtt

STAT_DISCONNECTED = 'disconnected'
STAT_CONNECTED = 'connected'
STAT_SUBSCRIBED = 'subscribed'

class MqttCli:
    def __init__(self, host, port):
        self.cli = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.cli.on_connect = self.on_connect
        self.cli.on_message = self.on_message
        self.cli.connect(host, port, 60)

        self.stat = 'disconnected'

    def on_connect(self, client, userdata, flags, rc, properties=None):
        print("Connected with result code "+str(rc))
        self.cli.subscribe("test")

    def on_message(self, client, userdata, message):
        print("message received " ,str(message.payload.decode("utf-8")))
        print("message topic=",message.topic)
        print("message qos=",message.qos)
        print("message retain flag=",message.retain)


    def subscribe(self, topic):
        self.cli.subscribe(topic)

    def publish(self, topic, message):
        self.cli.publish(topic, message)

    def loop(self):
        self.cli.loop(timeout=1.0)