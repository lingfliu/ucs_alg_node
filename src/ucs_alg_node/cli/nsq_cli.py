import nsq

class NsqCli:

    def __init__(self, host, port, topic='mq', username=None, passwd=None, on_message=None):
        self.host = host
        self.port = port
        self.username = username
        self.passwd = passwd
        self.on_message = on_message
        self.channel = 'nsq'
        self.topic = topic

        self.nsq = nsq
        self.rx = None
        self.tx = nsq.Writer(nsqd_tcp_addresses=[self.host + ':' + str(self.port)])

    def connect(self):
        self.nsq.run()

    def publish(self, msg):
        self.tx.pub(self.topic, msg)

    def message_handle(self, msg):
        if self.on_message:
            self.on_message(msg)

    def subscribe(self, topic):
        self.rx = nsq.Reader(message_handler=self.message_handle,
                             nsqd_tcp_addresses=[self.host + ':' + str(self.port)],
                             topic=topic,
                             channel=self.channel,
                             lookupd_poll_interval=15)

    def run(self):
        nsq.run()