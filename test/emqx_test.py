import time

import paho.mqtt.client as mqtt


addr = '62.234.16.239'
# addr = 'localhost'
port = 1883
cli = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
cli.id = 'node'
cli.username_pw_set('admin', 'vivi1234')

def on_connect(client, userdata, flags, rc, prop):
    print('connected')
    client.subscribe('test')
    client.publish('test', str(time.time_ns()))

def on_subscribe(client, userdata, mid, granted_qos, properties):
    print('subscribed')

def on_publish(client, userdata, mid, rc, properties):
    print('published')

def on_message(client, userdata, msg):
    print(time.time_ns(), 'received', msg.topic, msg.payload)

cli.on_connect = on_connect
cli.on_message = on_message
cli.on_publish = on_publish
cli.on_subscribe = on_subscribe

cli.connect(addr, port, keepalive=60, )

cli.loop_forever()
