import threading
import time
import random

from src.ucs_alg_node.utils import InterruptableThread, StoppableThread, current_time_milli, ThreadEx

arg_list = []

exc_task = None

def _task_stream(x):
    i = 0
    while True:
        print('running task:', 'stream', 'sleep for 1 sec', 'at', current_time_milli())
        time.sleep(1)
        yield i*x
        i += 1

def _task_batch(x, input=None):
    if not input is None:
        print('running task:', x, input, 'sleep for 1 sec', 'at', current_time_milli())
        time.sleep(1)
        return x+input
    else:
        print('running task:', x, input, 'sleep for 1 sec', 'at', current_time_milli())
        return x

def result_handling(stat, res):
    print('task stat', stat, 'handling result:', res)

def main():
    for i in range(10):
        arg_list.append(i)

    def next_input():
        if len(arg_list) > 0:
            x = arg_list.pop(0)
            return x
        else:
            return None

    # task_schedule = ThreadEx(_task_batch, args=(1,), input=next_input, mode='return', post_task=result_handling)
    task_schedule = ThreadEx(task=_task_stream, args=(1,), input=(), mode='yield', post_task=result_handling)
    task_schedule.start()

    while True:
        time.sleep(4)
        print('skipping')
        task_schedule.stop()
        break

    while True:
        print('post skipped')
        time.sleep(3)

if __name__ == '__main__':
    main()
    print('end of main()')




