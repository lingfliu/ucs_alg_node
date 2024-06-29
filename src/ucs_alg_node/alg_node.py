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

    """
    :param cfg: {
        'id': str, node id,
        'name': str, node name,
        'mode': str, 'stream' or 'batch',
        'max_task': int, max task in queue if in batch mode,
        'alg': Alg, algorithm instance,
        'model_dir': str, model directory, by default './model',
        'out': AlgSubmitter, submitter instance,
        'alg_id': str, algorithm id, only effective in batch mode
        'task_id': str, task id, only effective in stream mode,
    }
    """
    def __init__(self, max_task=10, cfg=None, task=None):
        if cfg:
            # see demo for config example
            self.id = cfg['id'] if 'id' in cfg else 'default'
            self.name = cfg['name'] if 'name' in cfg else 'default'
            self.mode = cfg['mode'] if 'mode' in cfg else 'batch'
            self.model_dir = cfg['model_dir'] if 'model_dir' in cfg else './model'

            # alg config
            self.alg = cfg['alg']
            if self.alg:
                self.alg.init()

            self.submitter = cfg['out']

            self.task = task

        else:
            self.mode = None
            self.alg = None
            self.alg_submitter = None
            self.task = task

        # thread config
        self.thrd_stream = None
        self.thrd_batch = None


        if self.mode == 'batch':
            self.task_queue = Queue(max_task)

    def start(self):
        if not self.alg:
            return -1

        self.submitter.start()
        if self.mode == 'stream':
            self.thrd_stream = StoppableThread(task=self._task_stream, mode='yield')
            self.thrd_stream.start()
            return 0
        elif self.mode == 'batch':
            self.thrd_queue = True
            self.thrd_batch = StoppableThread(task=self._task_batch, mode='return')
            self.thrd_batch.start()
            return 0
        else:
            return -1

    def stop(self):
        if self.thrd_batch:
            self.thrd_batch.stop()
        if self.thrd_stream:
            self.thrd_stream.stop()
        self.submitter.stop()

    def submit_task(self, alg_task):
        if self.mode == 'stream':
            # reload sources
            self.task = alg_task
            self.alg.sources = self.task.sources
            self.reload()
            return 0
        elif self.mode == 'batch':
            try:
                # throw exception if queue is full
                self.task_queue.put(alg_task, block=False)
                return 0
            except:
                print("task queue full")
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
                    'task_id': self.task['id'],
                    'alg_name': self.alg.name,
                    'alg_id': self.alg.id,
                    'task_ts': tic,
                    'result_ts': current_time_milli(),
                    'values': res.vals,
                    'descp': res.explain,
                    'stats': 'done',
                })
            else:
                self.publish_result({
                    'task_id': self.task['id'],
                    'alg_name': self.alg.name,
                    'alg_id': self.alg.id,
                    'task_ts': tic,
                    'result_ts': current_time_milli(),
                    'values': None,
                    'descp': None,
                    'stats': 'error',
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

        if self.mode == 'stream':
            if self.thrd_stream:
                self.thrd_stream.stop()
            self.thrd_stream = StoppableThread(task=self._task_stream, mode='yield')
            self.thrd_stream.start()
        elif self.mode == 'batch':
            if self.thrd_batch:
                self.thrd_batch.stop()
            self.thrd_batch = StoppableThread(task=self._task_batch, mode='return')
            self.thrd_batch.start()

    def publish_result(self, res):
        if self.submitter:
            ret = self.submitter.submit(res)
            if ret < 0:
                return -1
            else:
                return 0
        else:
            return -1