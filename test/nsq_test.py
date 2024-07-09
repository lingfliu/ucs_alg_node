# import time
#
# from src.ucs_alg_node.cli import NsqCli
#
host = '62.234.16.239'
# # host = 'localhost'
port = 4171
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

def handle_msg(msg):
    print('received: ', msg.body)
    return True
r = nsq.Reader(message_handler=handle_msg, nsqd_tcp_addresses=[host + ':4171'], topic='test_topic', channel='nsqxxd', lookupd_poll_interval=15)

nsq.run()