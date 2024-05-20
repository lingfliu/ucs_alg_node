import nsq

class MqCli:
    """MQ cli, by default, using NSQ
    """

    def __init__(self):
        self.rx = None

    def __int__(self, host, port, topic, channel):
        self.topic = topic
        self.host = host
        self.port = port
        self.channel = channel
        self.nsq = nsq
        self.rx = None
        self.tx = nsq.Writer(nsqd_tcp_addresses=[self.host + ':' + self.port])

    def connect(self):
        self.nsq.run()

    def publish(self, msg):
        self.nsq.pub(self.topic, msg)

    def message_handle(self, msg):
        if self.on_message:
            self.on_message(msg)

    def subscribe(self, topic):
        self.rx = nsq.Reader(message_handler=self.message_handle,
                             lookupd_http_addresses=[self.host + ':' + self.port],
                             topic=topic, channel=self.channel, lookupd_poll_interval=15)
