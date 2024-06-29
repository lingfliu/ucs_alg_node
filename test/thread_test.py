from src.ucs_alg_node.utils import InteruptableThread
import time

def _task(input):
    for i in range(10):
        time.sleep(0.1)
        print('task running', input, i)
    print('task done')


thrd = InteruptableThread(_task, ('input',))

thrd.start()

time.sleep(3)

thrd.skip()
print('thread stopped')
thrd.join()