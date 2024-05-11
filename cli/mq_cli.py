class MqCli:
    '''MQ class to connect, publish and subscribe to MQ
        by default, using NSQ
    '''

    def __int__(self):
        pass

    def connect(self):
        print("Connected to MQ")

    def publish(self, msg):
        print("Published to MQ")

    def subscribe(self, topic):
        print(f"Subscribed to {topic}")