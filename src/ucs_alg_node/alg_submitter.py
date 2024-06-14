from . import cli

from .utils import StoppableThread
from queue import Queue

MODE_MQ = 'mq'
MODE_DB = 'db'
MODE_API = 'api'


class AlgSubmitter:
    def __init__(self, dest, mode, username, passwd, topic, queue_max=100):
        self.dest = dest
        self.mode = mode
        self.username = username
        self.passwd = passwd
        self.topic = topic

        output_type = dest.split(':')[0]
        self.output_type = output_type
        if 'http' in output_type:
            self.mode = MODE_API
            self.submit_cli = cli.HttpCli(dest, '')
        elif 'mqtt' in output_type:
            self.mode = MODE_MQ
            host = dest.split(':')[1]
            port = dest.split(':')[2]
            self.submit_cli = cli.MqttCli(host, port, self.username, self.passwd, [self.topic])
        elif 'redis' in output_type:
            self.mode = MODE_DB
            host = dest.split(':')[1]
            port = dest.split(':')[2]
            self.submit_cli = cli.RedisCli(host, port, 0, self.username, self.passwd)
            # TODO redis im mq mode
            # if self.mode == MODE_DB:
            # elif self.mode == MODE_MQ:
            #     self.submit_cli = cli.RedisCli(dest, self.username, self.passwd)
        elif 'nsq' in output_type:
            self.mode = MODE_MQ
            host = dest.split(':')[1]
            port = dest.split(':')[2]
            self.submit_mode = cli.MqCli(host, port, self.topic, 0, self.username, self.passwd)
        else:
            self.submit_cli = None

        self.cli = None

        self.queue = Queue(maxsize=queue_max)
        self.thrd_queue = None

    def start(self):
        self.thrd_queue = StoppableThread(task=self._task_queue, mode='return')
        self.thrd_queue.start()

    def stop(self):
        self.thrd_queue.stop()

    def _task_queue(self):
        try:
            result = self.queue.get(block=False)
            ret = self._submit(result)
            if ret < 0:
                # todo log failed submission
                print('result submit failed', result)
                self.stats = 'offline'
                return None
            else:
                return 0
        except:
            # return None if get failed so the thread sleeps
            return None

    def submit(self, result):
        try:
            self.queue.put(result, block=False)
            return 0
        except:
            return -1


    def _submit(self, result):
        """
        submit result to mq or db
        :return 0 if success, -1 if failed
        """
        if not self.cli:
            return -1
        else:
            if self.output_type == 'http':
                return self.cli.submit(result.task_id, result)
            elif self.output_type == 'mqtt':
                return self.cli.publish(self.topic, {
                    'task_id': result.task_id,
                    'res': result
                })
            elif self.output_type == 'redis':
                return self.cli.set(result.task_id, result)
            elif self.output_type == 'nsq':
                return self.cli.publish({
                    'task_id': result.task_id,
                    'res': result
                })
            else:
                return -1
