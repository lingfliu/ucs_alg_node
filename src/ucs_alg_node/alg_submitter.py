import json
import os
import time

from . import cli

from .utils import StoppableThread, current_time_milli, InterruptableThread
from queue import Queue


MODE_MQ = 'mq'
MODE_DB = 'db'
MODE_API = 'api'


class AlgSubmitter:
    def __init__(self, dest, mode, username, passwd, topic, id=None, queue_max=100):
        # TODO: file cli config
        self.dest = dest
        self.mode = mode
        self.username = username
        self.passwd = passwd
        self.topic = topic
        self.id = id

        self.cli = None
        if mode == 'http':
            self.submit_cli = cli.HttpCli(dest)
        elif mode=='mqtt':
            host, port = dest.split(':')[0], int(dest.split(':')[1])

            self.cli = cli.MqttCli(host, port, self.username, self.passwd, id, [self.topic])
            self.cli.connect()
        elif mode == 'redis':
            # TODO redis im db mode
            # host = dest.split(':')[1]
            # port = dest.split(':')[2]
            # self.submit_cli = cli.RedisCli(host, port, 0, self.username, self.passwd)
            # TODO redis im mq mode
            # if self.mode == MODE_DB:
            # elif self.mode == MODE_MQ:
            #     self.submit_cli = cli.RedisCli(dest, self.username, self.passwd)
            pass
        elif mode=='nsq':
            #TODO nsq mq mode
            pass
            # self.submit_mode = cli.NsqCli(host, port, self.topic, 0, self.username, self.passwd)
        else:
            self.cli = None

        self.queue = Queue(maxsize=queue_max)
        self.thrd_queue = None

    def start(self):
        self.thrd_queue = InterruptableThread(target=self._task_queue)
        self.thrd_queue.start()

    def stop(self):
        self.thrd_queue.skip()

    def _task_queue(self):
        while True:
            try:
                result = self.queue.get(block=True)
                if result:
                    ret = self._submit(result)
                    print('submitting result:', result, 'result', ret)
                    if ret < 0:
                        # todo log failed submission
                        print('result submit failed', result)
                        self.stats = 'offline'
                    else:
                        print('submitted result:' + json.dumps(result))
                else:
                    print('no result in queue')
                    time.sleep(0.1)
            except:
                time.sleep(0.1)

    def submit(self, result):
        try:
            self.queue.put(result, block=True)
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
            # if result.has_key('file'):
            #     # upload file into minio
            #     fname = result['task_id'] + '_' + str(current_time_milli())
            #     res = self.file_cli.upload(fname, result['file'])
            #     if res >= 0:
            #         # convert local path to minio file name
            #         result['file'] = fname
            #         # remove local file
            #         os.remove(result['file'])
            #     else:
            #         # failed to upload file
            #         os.remove(result['file'])
            #         return -1

            #TODO: upload file if any
            if self.mode == 'mqtt':
                ret = self.cli.publish(msg=result)
                return ret
            else:
                #TODO other submitter
                return -1
