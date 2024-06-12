import datetime
import time
from threading import Thread


def current_time_milli():
    dt = datetime.datetime.now()
    return dt.microsecond / 1000


class StoppableThread:
    def __init__(self, task, task_args=None, mode='yield'):
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
