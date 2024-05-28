import datetime
from threading import Thread


def current_time_milli():
    dt = datetime.datetime.now()
    return dt.microsecond / 1000


class StoppableThread:
    def __init__(self, params, task):
        self.params = params
        self.task = task
        self.thrd = None
        self.is_running = False

    def start(self):
        self.is_running = True
        self.thrd = Thread(target=self._run_task)
        self.thrd.start()

    def _run_task(self):
        while self.is_running:
            self.task(self.params)

    def stop(self):
        self.is_running = False



