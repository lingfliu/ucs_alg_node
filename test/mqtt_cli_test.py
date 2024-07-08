from src.ucs_alg_node.cli import MqttCli

host = '62.234.16.239'
# host = 'localhost'
port = 1883

def on_message(topic, msg):
    print('received: ', topic, msg)

def on_connect():
    cli.publish('ucs/alg/res', 'hello')

cli = MqttCli(host, port, 'admin', 'vivi1234', ['ucs/alg/res'], 'node112')

def on_connect():
    cli.publish('ucs/alg/res', 'hello')
cli.connect()
cli.cli.loop_forever()
