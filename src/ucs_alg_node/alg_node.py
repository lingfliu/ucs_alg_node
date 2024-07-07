import time

from .utils import current_time_milli

from .alg import Alg
from .alg_submitter import AlgSubmitter

from queue import Queue
from .utils import ThreadEx

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

            self.alg_timeout = cfg['alg_timeout'] if 'alg_timeout' in cfg else None
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

        def input():
            try:
                alg_task = self.task_queue.get(block=True)
                return alg_task
            except:
                return None

        self.submitter.start()
        if self.mode == 'stream':
            self.thrd_stream = ThreadEx(task=self._task_stream, args=(), mode='yield', post_task=self.publish_result)
            self.thrd_stream.start()
            return 0
        elif self.mode == 'batch':
            self.thrd_queue = True
            self.thrd_batch = ThreadEx(task=self._task_batch, args=(), input=input, mode='return', timeout=self.alg_timeout, post_task=self.publish_result)
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

    def skip(self):
        if self.mode == 'batch':
            self.thrd_batch.skip()
            return 0
        else:
            # stream mode does not support skipping
            return -1

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
        self.task.ts = current_time_milli()
        for ret in self.alg.infer_stream():
            result = self.wrap_result(self.task, ret)
            self.task.ts = current_time_milli()
            yield result

    def _task_batch(self, alg_task):
        """runs only in batch mode"""
        self.execute_task = alg_task
        alg_task.stats = 'running'
        ret = self.alg.infer_batch(alg_task)
        # wrap result with task infos
        result = self.wrap_result(alg_task, alg_task.tic, ret)
        return result

    def wrap_result(self, task, ret):
        """
        wrap result with task infos
        :param task: 
        :param tic: time of execution
        :param ret: result from alg
        :return:
        """
        if ret and ret.vals:
            result = {
                'task_id': task.id,
                'alg_name': self.alg.name,
                'alg_id': self.alg.id,
                'task_ts': task.ts,
                'result_ts': current_time_milli(),
                'values': ret.vals,
                'descp': ret.explain if ret.explain else '',
                'stats': 'done',
            }
        else:
            result = {
                'task_id': task['id'],
                'alg_name': self.alg.name,
                'alg_id': self.alg.id,
                'task_ts': task.ts,
                'result_ts': current_time_milli(),
                'values': None,
                'descp': '',
                'stats': 'error',
            }

        return result

    def reload(self):

        if self.alg:
            self.alg.reload()

        if self.mode == 'stream':
            self.thrd_stream = ThreadEx(task=self._task_stream, args=(), mode='yield', timeout=self.alg_timeout,
                                        post_task=self.publish_result)
            self.thrd_stream.start()
            return 0
        elif self.mode == 'batch':
            self.thrd_queue = True
            self.thrd_batch = ThreadEx(task=self._task_batch, args=(), input=input, mode='return',
                                       timeout=self.alg_timeout, post_task=self.publish_result)
            self.thrd_batch.start()
            return 0
        else:
            return -1

    def publish_result(self, ret):
        if self.submitter:
            ok = self.submitter.submit(ret)
            if ok < 0:
                return -1
            else:
                return 0
        else:
            return -1