import asyncio
import os
import datetime
import threading
import time
from threading import Thread
import ctypes


def current_time_milli():
    ms = time.time_ns()/1000000
    return ms

def get_cwd():
    return os.getcwd()


class StoppableThread:
    """
    Deprecated
    """
    def __init__(self, task, task_args=None, mode='return'):
        self.task = task
        self.task_args = task_args
        self.thrd = None
        self.is_running = False
        self.mode = mode

    def start(self):
        self.is_running = True
        self.thrd = Thread(target=self._run_task)
        self.thrd.start()

    def _run_task(self):
        if self.mode == 'return':
            while self.is_running:
                if self.task_args:
                    res = self.task(self.task_args)
                else:
                    res = self.task()

                if not res:
                    time.sleep(0.1)

        elif self.mode == 'yield':
            while self.is_running:
                if self.task_args:
                    for _ in self.task(self.task_args):
                        if not self.is_running:
                            break
                else:
                    for _ in self.task():
                        if not self.is_running:
                            break

    def stop(self):
        self.is_running = False

class InterruptableThread(Thread):
    def __init__(self, target, args=(), timeout=None, mode='return'):
        Thread.__init__(self, target=target, args=args)
        self._target = target
        self._args = args
        self.timeout = timeout
        self.stat = 'idle'
        self.ret = None
        self.mode = mode

    def run(self):
        # todo: yield task
        tic = time.time()
        self.stat = 'running'
        try:
            if self.mode == 'return':
                self.ret = self._target(*self._args)
                self.stat = 'done'
                return
            elif self.mode == 'yield':
                self._target(*self._args)
        finally:
            # thread stopped
            toc = time.time()
            if not self.timeout is None:
                if toc - tic > self.timeout:
                    self.stat = 'timeout'

    def get_id(self):
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id

    def skip(self):
        thread_id = self.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, ctypes.py_object(SystemExit))
        if res == 0:
            # raise ValueError('invalid thread id')

            # thread already finished
            pass
        elif res != 1:
            # if it returns a number greater than one, you're in trouble,
            # and you should call it again with exc=NULL to revert the effect
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            raise SystemError('PyThreadState_SetAsyncExc failed')

class ThreadEx(Thread):
    """a simple thread extension supporting:
    1. return & yield mode
    2. task skip & stop
    3. timeout handling
    """
    def __init__(self, task, args=(), input=None, mode="return", timeout=None, post_task=None):
        Thread.__init__(self, target=task, args=args)
        self._target = task
        # if in return mode, args should be iterable
        self._args = args

        self.input = input
        self.mode = mode
        self.timeout = timeout

        self.post_task = post_task

        self.is_running = True
        self.stat = 'idle'
        self.exc_task = None

    def _input_bind_task(self, task, args, input):
        if input is not None:
            return task(*args, input)
        else:
            return task(*args)

    def _yield_task(self, task, args):
        for x in task(*args):
            self.post_task(x)

    def run(self):
        self.stat = 'running'
        if self.mode == 'return':
            while self.is_running:
                if not self.input:
                    self.is_running = False
                    break

                x = self.input()
                if not x:
                    # all tasks done, quit the loop
                    # self.is_running = False
                    # break
                    time.sleep(0.1)
                else:

                    self.exc_task = InterruptableThread(self._input_bind_task, (self._target, self._args, x))
                    self.exc_task.start()
                    self.exc_task.join(timeout=self.timeout)
                    self.stat = self.exc_task.stat
                    self.post_task(self.exc_task.ret)

        elif self.mode == "yield":
            while self.is_running:
                self.exc_task = InterruptableThread(self._yield_task, (self._target, self._args), mode='yield')
                self.exc_task.start()
                self.exc_task.join(timeout=self.timeout) # will not timeout until stop is called

    def skip(self):
        if self.exc_task:
            self.exc_task.skip()
        self.stat = 'skip'

    def stop(self):
        self.is_running = False
        self.skip()
        self.stat = 'stop'


class CoroutineThread(Thread):
    def __init__(self, target, args=(), timeout=None):
        Thread.__init__(self, target=target, args=args)

        new_loop = asyncio.new_event_loop()
        self._target = target
        self._args = args
        self.timeout = timeout
        self.stat = 'idle'
        self.ret = None

        self.loop = asyncio.get_event_loop()

    def run(self):
        task = asyncio.ensure_future(self._target(*self._args))
        self.loop.run_until_complete(task)

    def skip(self):
        self.stat = 'skip'