import time
import redis
from threading import Thread


STAT_DISCONNECTED = 'disconnected'
STAT_CONNECTED = 'connected'
STAT_CONNECTING = 'connecting'


class RedisCli:
    """redis client for result submission"""
    def __init__(self, host, port, db, username, passwd):
        self.host = host
        self.port = port
        self.db = db
        self.username = username
        self.passwd = passwd

        self.r = None

        self.stat = STAT_DISCONNECTED

    def connect(self):
        Thread(target=self._connect).start()

    def _connect(self):
        self.stat = STAT_CONNECTING
        r = redis.Redis(host=self.host, port=self.port, db=self.db, password=self.passwd, username=self.username, socket_keepalive=True)
        if r.ping():
            self.stat = STAT_CONNECTED
            self.r = r
        else:
            self.stat = STAT_DISCONNECTED

    def get(self, key):
        if self.stat == STAT_CONNECTED:
            res = self.r.get(key)
            if res:
                return res
            else:
                self.on_failed()
                return None
        else:
            return None

    def set(self, key, value):
        if self.stat == STAT_CONNECTED:
            return self.r.set(key, value)
        else:
            return -1

    def delete(self, key):
        if self.stat == STAT_CONNECTED:
            return self.r.delete(key)
        else:
            return -1

    def on_failed(self):
        self.stat = STAT_DISCONNECTED
        time.sleep(0.01)
        self.connect()