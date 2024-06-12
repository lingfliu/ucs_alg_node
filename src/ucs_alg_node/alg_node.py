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
            # see demo for config example
            self.id = cfg['id'] if 'id' in cfg else 'default'
            self.name = cfg['name'] if 'name' in cfg else 'default'
            self.mode = cfg['mode'] if 'mode' in cfg else 'batch'
            self.model_dir = cfg['model_dir'] if 'model_dir' in cfg else './model'

            # thread config
            self.thrd_stream = None
            self.thrd_queue = None

            # alg config
            self.alg_task_id = cfg['alg_task_id'] if 'alg_task_id' in cfg else 'default'
            self.alg = cfg['alg']
            if self.alg:
                self.alg.prepare()

            self.submitter = cfg['out']

        else:
            self.mode = None
            self.alg = None
            self.alg_submitter = None

        self.execute_task = None

        if self.mode == 'batch':
            self.task_queue = Queue(max_task)

    def run(self):
        if not self.alg:
            return -1

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

    def submit_task(self, alg_task):
        if self.mode == 'stream':
            # reload sources
            self.execute_task = alg_task
            self.alg.sources = alg_task.sources
            self.alg.reload()
            return 0
        elif self.mode == 'batch':
            try:
                # throw exception if queue is full
                self.task_queue.put(alg_task, block=False)
                return 0
            except:
                return -1
        else:
            return -1

    def set_model(self, model):
        # alg will handle model reloading
        self.alg.model = model
        self.reload()

    def _task_stream(self):
        """simply call infer_stream without args"""
        tic = current_time_milli()
        for res in self.alg.infer_stream():
            # wrap result with task infos
            if res:
                self.publish_result({
                    'task_id': self.alg_task_id,
                    'alg_name': self.alg.name,
                    'alg_id': self.alg.id,
                    'task_ts': tic,
                    'result_ts': current_time_milli(),
                    'stats': res,
                })
            else:
                self.publish_result({
                    'task_id': self.alg_task_id,
                    'alg_name': self.alg.name,
                    'alg_id': self.alg.id,
                    'task_ts': tic,
                    'result_ts': current_time_milli(),
                    'stats': 'failed',
                })
            yield res
            tic = current_time_milli()

    def _task_batch(self):
        """runs only in batch mode"""
        try:
            alg_task = self.task_queue.get(block=False)

            self.execute_task = alg_task
            alg_task.stats = 'running'
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
        except:
            return None


    def reload(self):
        if self.alg:
            self.alg.reload()

    def publish_result(self, res):
        if self.submitter:
            ret = self.submitter.submit(res)
            if ret < 0:
                return -1
            else:
                return 0
        else:
            return -1

    def check_task(self, task_id):
        """
        check task status in one of: 'pending', 'error', 'running', 'done', 'unknown'
        todo: store task status in local db
        """
        if self.execute_task.id == task_id:
            return 'running'

        for idx, task in enumerate(self.task_queue.queue):
            if task.id == task_id:
                return 'pending'

        return 'unknown'


