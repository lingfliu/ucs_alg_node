import datetime
from threading import Thread


def current_time_milli():
    dt = datetime.datetime.now()
    return dt.microsecond / 1000

class SimpleThread:
    def __init__(self, params, task):
        self.params = params
        self.task = task
        self.thrd = Thread(target=self.task)

