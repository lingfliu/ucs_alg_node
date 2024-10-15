import os
import threading
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
            self.model_dir = cfg['model_dir'] if 'model_dir' in cfg else os.path.join(os.getcwd(), 'models')

            if not os.path.exists(self.model_dir):
                os.makedirs(self.model_dir)

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
            self.task_list = []
            self.max_task = max_task
            self.task_list_lck = threading.RLock()

    def start(self):
        # TODO: validate alg
        if not self.alg:
            return -1

        '''define the input function for batch mode only'''
        def input():
            alg_task = self.pop_task()
            return alg_task


        self.submitter.start()
        if self.mode == 'stream':
            self.thrd_stream = ThreadEx(task=self._task_stream, args=(), mode='yield', post_task=self.publish_result)
            self.thrd_stream.start()
            return 0
        elif self.mode == 'batch':
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
            # task update not supported in stream mode
            return -1
        elif self.mode == 'batch':
            ret = self.push_task(alg_task)
            if ret < 0:
                print("task queue full")
                return -2
            else:
                print('task in queue, queue size:', len(self.task_list))
                return 0
        else:
            return -3 # unknown mode

    """push the task at the tail of the queue (FIFO)"""
    def push_task(self, alg_task):
        self.task_list_lck.acquire()
        if len(self.task_list) >= self.max_task:
            self.task_list_lck.release()
            return -1
        else:
            alg_task.stats = 'pending'
            self.task_list.append(alg_task)
            self.task_list_lck.release()
            return 1

    """push the task at the head of the queue (LIFO)"""
    def headpush_task(self, alg_task):
        self.task_list_lck.acquire()
        if len(self.task_list) >= self.max_task:
            self.task_list_lck.release()
            return -1
        else:
            alg_task.stats = 'pending'
            self.task_list = [alg_task] + self.task_list
            self.task_list_lck.release()
            return 1

    def pop_task(self):
        self.task_list_lck.acquire()
        if len(self.task_list) > 0:
            task = self.task_list.pop(0)
            task.stats = 'running'
            self.task_list_lck.release()
            return task
        else:
            self.task_list_lck.release()
            return None

    """reorder the task at pos to idx=reorder"""
    def reorder_task(self, pos, reorder):
        self.task_list_lck.acquire()
        if pos >= len(self.task_list) or reorder >= len(self.task_list):
            self.task_list_lck.release()
            return -1

        # move the task at pos to reorder
        new_task_list = []
        for idx in range(len(self.task_list)):
            if idx == reorder:
                new_task_list.append(self.task_list[pos])
            else:
                if idx != pos:
                    new_task_list.append(self.task_list[idx])

        self.task_list = new_task_list
        self.task_list_lck.release()
        return 0

    """only take effect when the model file is in model_dir"""
    def set_model(self, model_fname):
        # alg will handle model reloading
        """check if model exists in model_dir, if not download it"""
        if os.path.exists(os.path.join(self.model_dir, model_fname)):
            self.alg.model = model_fname
            self.reload()
            return 0
        else:
            return -1

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
        result = self.wrap_result(alg_task, ret)
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

    """publish result to a given submitter or stdout"""
    def publish_result(self, ret, task_stat):
        if task_stat == 'timeout':
            ret['stats'] = 'timeout'
        if self.submitter:
            ok = self.submitter.submit(ret)
            if ok < 0:
                print("result:", ret)
        else:
            # output to console
            print("result:", ret)