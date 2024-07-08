import time

import paho.mqtt.client as mqtt

from ..utils import InterruptableThread

STAT_DISCONNECTED = 'disconnected'
STAT_CONNECTING = 'connecting'
STAT_CONNECTED = 'connected'

class MqttCli:
    def __init__(self, host, port, username, passwd, id, topics=None):
        self.host = host
        self.port = port
        self.username = username
        self.passwd = passwd
        self.id = id
        if topics:
            self.topics = topics
        else:
            self.topics = []

        self.cli = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.cli.username_pw_set(username, passwd)
        self.cli.id = id
        self.stat = STAT_DISCONNECTED

        self.msg_cb = {}

        self.active_disconnect = False
        self.thrd_conn = None

        self.cli.on_connect = self._on_connect
        self.cli.on_message = self._on_msg

    def connect(self):
        self.stat = STAT_CONNECTING
        self.cli.connect(self.host, self.port, 60)
        return 0

    def reconnect(self):
        self.connect()

    def disconnect(self):
        self.active_disconnect = True
        self.stat = STAT_DISCONNECTED
        self.cli.disconnect()
        return 0

    def publish(self, topic=None, msg=None):
        """
        :param topic:
        :param msg:
        :return: -1 if arg check failed
        """
        if not topic:
            if len(self.topics) > 0:
                if msg:
                    self.cli.publish(self.topics[0], msg)
                    return 0
                else:
                    return -1
            else:
                return -1
        else:
            if msg:
                self.cli.publish(topic, msg)
                return 0
            else:
                return -1
    def subscribe(self,topic, on_msg=None):
        self.cli.subscribe(topic)
        self.msg_cb[topic] = on_msg

    def _on_connect(self, client, userdata, flags, rc, prop):
        if rc == 'Success':
            print("Connected to MQTT Broker!")
            self.stat = STAT_CONNECTED
            for topic in self.topics:
                self.cli.subscribe(topic)
        else:
            print("Failed to connect, return code %d\n", rc)
            self.stat = STAT_DISCONNECTED

    def _on_disconnect(self, client, userdata, rc, prop):
        print("Disconnected from MQTT Broker!")
        self.stat = STAT_DISCONNECTED
        time.sleep(0.01)
        # auto-reconnect
        if not self.active_disconnect:
            self.reconnect()

    def _on_msg(self, client, userdata, msg):
        print('received', msg.topic + " " + str(msg.payload))


    def _task_net(self):
        while self.stat != STAT_CONNECTED:
            time.sleep(0.05)

        self.cli.loop_forever()

    def start(self):
        self.thrd_conn = InterruptableThread(target=self._task_net)
        self.thrd_conn.start()

    def stop(self):
        self.thrd_conn.stop()
        self.cli.disconnect()