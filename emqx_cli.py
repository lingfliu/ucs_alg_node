# 发送
import random
import time
import paho.mqtt.client as mqtt_client

topic = "/python/mqtt"  # 创建话题，可以自定义
client_id = f'python-mqtt-{random.randint(0, 100)}'  # 获取随机id（可以自行选择）
username = 'username'
password = 'password'
def publish(client):  # 发布的核心方法
    msg_count = 0
    while True:
        time.sleep(1)
        msg = f"messages: {msg_count}"  # 发送的消息（message）
        result = client.publish(topic, msg)  # 调用库中方法public（）进行发布，会返回一个列表
        status = result[0]  # 列表的第一个元素返回的是请求是否成功，然后作判断
        if status == 0:
            print(f"Send `{msg}` to topic `{topic}`")
        else:
            print(f"Failed to send message to topic {topic}")
        msg_count += 1

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1,client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(host='127.0.0.1', port=18083)  # #此处不需要更改，都为默认
    return client

def run():
    client = connect_mqtt()
    client.loop_start()
    publish(client)


if __name__ == '__main__':
    run()
# 接收
# import random
# from paho.mqtt import client as mqtt_client
#
# topic = "/python/mqtt"
# client_id = f'python-mqtt-{random.randint(0, 100)}'
#
#
# def connect_mqtt() -> mqtt_client:
#     def on_connect(client, userdata, flags, rc):
#         if rc == 0:
#             print("Connected to MQTT Broker!")
#         else:
#             print("Failed to connect, return code %d\n", rc)
#
#     client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1,client_id)
#     client.on_connect = on_connect
#     client.connect(host='127.0.0.1', port=18083)
#     return client
#
#
# def subscribe(client: mqtt_client):
#     def on_message(client, userdata, msg):
#         print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
#
#     client.subscribe(topic)
#     client.on_message = on_message
#
#
# def run():
#     client = connect_mqtt() # 创建mqtt对象
#     subscribe(client)
#     client.loop_forever() # 表示永久等待发布者发布消息
#
#
# if __name__ == '__main__':
#     run()
#

