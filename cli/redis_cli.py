import redis

class RedisCli:
    """redis client for result submission"""
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def connect(self):
        """todo db configuration"""
        return redis.StrictRedis(host=self.host, port=self.port, db=0)

    def get(self, key):
        return self.connect().get(key)

    def set(self, key, value):
        return self.connect().set(key, value)

    def delete(self, key):
        return self.connect().delete(key)

    def submit(self, tid, result):
        """ result submission"""
        return self.connect().set(tid, result)