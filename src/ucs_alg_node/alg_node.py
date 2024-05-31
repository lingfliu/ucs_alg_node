import time

from .utils import current_time_milli

from .alg import Alg
from .alg_submitter import AlgSubmitter

from queue import Queue
from .utils import StoppableThread

ALG_STATE_IDLE = 0
ALG_STAT_PREPARE = 1 # alg is restarting or downloading model
ALG_STATE_RUNNING = 2
ALG_STATE_ERROR = 3


class AlgNode:
    def __init__(self, max_task=10, cfg=None):
        if cfg:
            # node config
            self.id = cfg['id'] if 'id' in cfg else 'default'
            self.name = cfg['name'] if 'name' in cfg else 'default'
            self.mode = cfg['mode'] if 'mode' in cfg else 'batch'
            self.model_dir = cfg['model_dir'] if 'model_dir' in cfg else './model'

            # stub config
            self.thrd_stream = None
            self.thrd_queue = None

            # alg config
            self.alg_task_id = cfg['alg_task_id'] if 'alg_task_id' in cfg else 'default'
            self.alg = cfg['alg']
            if self.alg:
                self.alg.prepare()

            self.submitter = cfg['out']

        else:
            self.alg = None
            self.alg_submitter = None

        if self.mode == 'batch':
            self.task_queue = Queue(max_task)

    def run(self):
        self.submitter.start()
        if self.mode == 'stream':
            self.thrd_stream = StoppableThread(task=self._task_stream)
            self.thrd_stream.start()
            return 0
        elif self.mode == 'batch':
            self.thrd_queue = True
            self.thrd_queue = StoppableThread(task=self._task_batch)
            self.thrd_queue.start()
            return 0
        else:
            return -1

    def stop(self):
        if self.thrd_queue:
            self.alg.stop()
            self.thrd_queue.stop()
        if self.thrd_stream:
            self.alg.stop()
            self.thrd_stream.stop()
        self.submitter.stop()

    def _task_stream(self):
        """simply call infer_stream without args"""
        tic = current_time_milli()
        for res in self.alg.infer_stream():
            # wrap result with task infos
            if res:
                self.publish_result({
                    'task_id': self.alg_task_id,
                    'task_ts': tic,
                    'result_ts': current_time_milli(),
                    'res': res,
                })
            else:
                self.publish_result({
                    'task_id': self.alg_task_id,
                    'task_ts': tic,
                    'result_ts': current_time_milli(),
                    'res': 'failed',
                })
            yield res

    def submit_task(self, alg_task):
        if self.mode != 'batch':
            return -1
        else:
            self.task_queue.put(alg_task, block=True, timeout=5)
            return 0

    def _task_batch(self):
        """runs only in batch mode"""
        if self.task_queue.empty():
            return None

        alg_task = self.task_queue.get()
        res = self.alg.infer_batch(alg_task)
        # wrap result with task infos
        if res:
            self.publish_result({
                'task_id': alg_task.id,
                'task_ts': alg_task.ts,
                'result_ts': current_time_milli(),
                'res': res,
            })
        else:
            self.publish_result({
                'task_id': alg_task.id,
                'res': 'failed',
            })

    def reload(self):
        if self.alg:
            self.alg.reload()

    def publish_result(self, res):
        if self.submitter:
            self.submitter.submit(res)
            return 0
        else:
            return -1

    def check_task(self, task_id):
        """check task status"""
        for idx, task in enumerate(self.task_queue.queue):
            if task.id == task_id:
                return idx

        return -1


