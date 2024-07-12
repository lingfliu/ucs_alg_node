import time
import json

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

        def _on_connect(client, userdata, flags, rc, prop):
            if rc == 'Success':
                print("connected to Emqx")
                self.stat = STAT_CONNECTED
                for topic in self.topics:
                    self.cli.subscribe(topic)
            else:
                print("failed to connect, return code %d\n", rc)
                self.stat = STAT_DISCONNECTED

        def _on_disconnect(client, userdata, df, rc, prop):
            # print("Disconnected from MQTT Broker!")
            self.stat = STAT_DISCONNECTED

        def _on_subscribe(client, userdata, mid, rc, properties):
            pass
            # print("Subscribed to topic with %s" % rc[0])

        def _on_publish(client, userdata, mid, rc, properties):
            pass
            # print("Published message with mid %d" % mid)

        def _on_msg(client, userdata, msg):
            # print('received', msg.topic + " " + str(msg.payload))
            if msg.topic in self.msg_cb:
                self.msg_cb[msg.topic](msg.topic, msg.payload)

        self.cli.on_connect = _on_connect
        self.cli.on_message = _on_msg
        self.cli.on_disconnect = _on_disconnect
        self.cli.on_subscribe = _on_subscribe
        self.cli.on_publish = _on_publish

    def connect(self):
        self.stat = STAT_CONNECTING
        self.cli.connect(self.host, self.port, 10)
        self.cli.loop_start()
        return 0

    def disconnect(self):
        self.active_disconnect = True
        self.stat = STAT_DISCONNECTED
        self.cli.disconnect()
        self.cli.loop_stop()
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
                    ret = self.cli.publish(self.topics[0], json.dumps(msg))
                    ret.wait_for_publish(timeout=1)
                    return 0
                else:
                    return -1
            else:
                return -1
        else:
            if msg:
                ret = self.cli.publish(topic, json.dumps(msg))
                ret.wait_for_publish(timeout=10)
                return 0
            else:
                return -1

    def subscribe(self,topic, on_msg=None):
        self.cli.subscribe(topic)
        self.msg_cb[topic] = on_msg

    def start(self):
        if self.stat != STAT_CONNECTED:
            return
        self.thrd_conn = InterruptableThread(target=self._task_net)
        self.thrd_conn.start()

    def stop(self):
        if self.stat == STAT_DISCONNECTED:
            return
        else:
            self.stat = STAT_DISCONNECTED
            self.cli.disconnect()
            if self.thrd_conn:
                self.thrd_conn.stop()