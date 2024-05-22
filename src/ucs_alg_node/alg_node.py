import time

import utils

from alg import Alg
from alg_submitter import AlgSubmitter

import threading
from queue import Queue

ALG_STATE_IDLE = 0
ALG_STAT_PREPARE = 1 # alg is restarting or downloading model
ALG_STATE_RUNNING = 2
ALG_STATE_ERROR = 3


class AlgNode:
    def __init__(self, max_task=10, cfg=None):
        if cfg:
            self.id = cfg['id'] if 'id' in cfg else 'default'
            self.name = cfg['name'] if 'name' in cfg else 'default'
            self.mode = cfg['mode'] if 'mode' in cfg else 'batch'

            if 'alg' in cfg:
                alg_cfg = cfg['alg']
                # provide model's url if the model has to be specified or downloaded
                self.alg = Alg(self.mode, alg_cfg['sources'], alg_cfg['model'])
            else:
                self.alg = None

            if 'out' in cfg:
                out_cfg = cfg['out']
                self.submitter = AlgSubmitter(
                    dest=out_cfg['dest'],
                    mode=out_cfg['mode'],
                    username=out_cfg['username'],
                    passwd=out_cfg['passwd'],
                    topic=out_cfg['topic'] # if in db mode, can be omitted
                )
            else:
                self.submitter = None

            self.alg.load_model()

        else:
            self.alg = None
            self.alg_submitter = None

        self.is_running = True

        if self.mode == 'batch':
            self.task_queue = Queue(max_task)
            threading.Thread(target=self._task_infer).start()

    def run(self):
        if self.mode == 'stream':
            self.is_running = True
            threading.Thread(target=self._task_stream).start()

    def _task_stream(self):
        """task loop only for stream mode"""
        for res in self.alg.infer():
            self.publish_result(res)
            if not self.is_running: # loop control
                break

    def submit_task(self, alg_task):
        if self.mode != 'batch':
            return -1
        else:
            self.task_queue.put(alg_task, block=True, timeout=5)
            return 0

    def _task_infer(self):
        """runs only in batch mode"""
        while True:
            if self.task_queue.empty():
                time.sleep(1)
            else:
                alg_task = self.task_queue.get()
                res = self.alg.infer_batch(alg_task)
                # wrap result with task infos
                if res:
                    self.publish_result({
                        'tid': alg_task.tid,
                        'task_ts': alg_task.ts,
                        'result_ts': utils.current_time_milli(),
                        'res': res,
                    })
                else:
                    self.publish_result({
                        'tid': alg_task.tid,
                        'res': 'failed',
                    })
            if not self.is_running:
                break

    def reload(self):
        if self.alg:
            self.alg.reload()

    def publish_result(self, res):
        self.submitter.submit(res)



