import time

from src.ucs_alg_node.cli import MqttCli
from src.ucs_alg_node.utils import InterruptableThread

host = '62.234.16.239'
# host = 'localhost'
port = 1883
default_topic = 'ucs/alg/result'

def on_message(topic, msg):
    tic = int(msg['msg']['ts'])
    toc = time.time_ns()
    print('received: ', topic, msg, 'at %d'%time.time_ns(), 'latency: %d ns'%(toc - tic))


cli = MqttCli(host, port, 'admin', 'vivi1234', 'node112', [default_topic, ])
cli.connect()

def _task_publish():
    i = 0
    while True:
        if cli.stat != 'connected':
            time.sleep(0.05)
        cli.publish(default_topic, {
            'result': 'ok',
            'msg': {
                'time': time.time_ns(),
                'value': [a for a in range(10) ]
            }
        })
        i += 1
        time.sleep(0.01)

# thrd_pub = InterruptableThread(target=_task_publish)
# thrd_pub.start()

def _task_subscribe():
    while cli.stat != 'connected':
        time.sleep(0.05)
    cli.subscribe(default_topic, on_message)

thrd_sub = InterruptableThread(target=_task_subscribe)
thrd_sub.start()

while True:
    time.sleep(10)

    print('disconnecting')
    # thrd_pub.skip()
    # thrd_sub.skip()
    # cli.disconnect()
    # break