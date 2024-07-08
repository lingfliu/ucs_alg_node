import nsq
import time
import tornado.ioloop
import json
class MqCli:
    """MQ cli, by default, using NSQ
    """

    def __init__(self, host, port, topic, channel, username, passwd, on_message=None):
        self.topic = topic
        self.host = host
        self.port = port
        self.channel = channel
        self.username = username
        self.passwd = passwd
        self.on_message = on_message

        self.nsq = nsq

        self.tx = nsq.Writer(nsqd_tcp_addresses=[self.host + ':' + str(self.port)])

        self.rx = None
    def connect(self):

        self.nsq.run()

    def publish(self, msg):
        msg = json.dumps(msg).encode('utf-8')
        # 发布消息
        self.tx.pub(self.topic, msg, print(msg))

    def message_handle(self, msg):
        if self.on_message:
            self.on_message(msg)
        print(msg)
        print(msg.body)

    def subscribe(self, topic=None):
        if topic is None:
            topic = self.topic
        self.rx = nsq.Reader(
            message_handler=self.message_handle,
            nsqd_tcp_addresses=[self.host + ':' + str(self.port)],
            topic=topic,
            channel=self.channel,
            lookupd_poll_interval=15
        )