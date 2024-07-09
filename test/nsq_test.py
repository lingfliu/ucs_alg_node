# import time
#
# from src.ucs_alg_node.cli import NsqCli
#
# host = '62.234.16.239'
# host = '192.168.0.103'
import time

host = 'localhost'

import tornado.ioloop

#
# default_topic = 'ucs/alg/result'
# def on_msg(msg):
#     print('received: ', msg)
#
# cli = NsqCli(host, port, default_topic, on_message=on_msg)
# print('runs here')
#
# cli.run()
#
# time.sleep(2)
#
# cli.subscribe(default_topic)
# cli.publish('hello')
#
# while True:
#     time.sleep(1)

import nsq
from src.ucs_alg_node.utils import InterruptableThread

def handle_msg(msg):
    # print('received: %s at '%msg.body + str(time.time_ns()))
    tic = int(msg.body.split(b':')[1])
    toc = time.time_ns()
    print('latency: %d ns'%(toc - tic))
    return True
r = nsq.Reader(message_handler=handle_msg, nsqd_tcp_addresses=[host + ':4150'], topic='test', channel='ucs', lookupd_poll_interval=15)

w = nsq.Writer([host + ':4150'])

def _on_pub_finished(conn, data):
    # print(data)
    pass

def _pub_task():
    for _ in range(1):
        w.pub('test', bytes('ts:%d'%time.time_ns(), 'utf-8'), _on_pub_finished)

tornado.ioloop.PeriodicCallback(_pub_task, 1).start()

nsq.run()
while True:
    time.sleep(1)