import datetime
import threading
import time
from threading import Thread
import ctypes


def current_time_milli():
    dt = datetime.datetime.now()
    return dt.microsecond / 1000


class StoppableThread:
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

class InteruptableThread(Thread):
    def __init__(self, target, args):
        Thread.__init__(self, target=target, args=args)
        self._target = target
        self._args = args


    def run(self):
        try:
            self._target(*self._args)
        finally:
            # thread stopped
            pass

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
