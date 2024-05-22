from cli import *
from minio import Minio
# mqtt_cli test
import random
import time
import paho.mqtt.client as mqtt_client
def test_mqtt_cli():
    mqtt_cli = MqttCli({

    })

    def on_connect():
        print('connected to EMQX')
    mqtt_cli.on_connect = on_connect

    mqtt_cli.loop()

    mqtt_cli.subscribe('ucs/alg/res')
    mqtt_cli.publish('ucs/alg/res', {
        'status': 'ok',
        'msg': 'connected'
    })

    # 订阅以及发布
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

    def subscribe(client: mqtt_client):
        def on_message(client, userdata, msg):
            print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

        client.subscribe(topic)
        client.on_message = on_message
    def connect_mqtt():
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
            else:
                print("Failed to connect, return code %d\n", rc)

        client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1, client_id)
        client.username_pw_set(username, password)
        client.on_connect = on_connect
        client.connect(host='127.0.0.1', port=18083)  # #此处不需要更改，都为默认
        return client
    client = connect_mqtt()
    client.loop_start()
    publish(client)# 发布
    # subscribe(client) # 订阅
    # client.loop_forever() # 表示永久等待发布者发布消息
def test_redis_cli():
    redis_cli = RedisCli({})

    redis_cli.connect()

    redis_cli.set('test', 'test')
    redis_cli.get('test')


def test_mq_cli():
    mq_cli = MqCli({
        'host': 'localhost:9092',
        'topic': 'test',
        'channel': 'test'
        })
def test_minio_cli():
    # Create a client with the MinIO server playground, its access key 使用MinI0服务器游乐场及其访问密钥创建客户端
    # and secret key.
    client = Minio(
        # endpoint指定的是你Minio的远程IP及端口
        endpoint="127.0.0.1:9090",
        access_key="admin",
        secret_key="admin1234",
        # 建议为False
        secure=False
    )

    # The file to upload, change this path if needed 本地文件上传
    source_file = r"D:\py program\ucs_alg_node\requirements.txt"

    # The destination bucket and filename on the MinIO server 保存在public下的requirements.txt
    bucket_name = "pubilc"
    destination_file = "requirements.txt"

    # Make the bucket if it doesn't exist.判断是否存在bucket_name
    found = client.bucket_exists(bucket_name)
    if not found:
        client.make_bucket(bucket_name)
        print("Created bucket", bucket_name)
    else:
        print("Bucket", bucket_name, "already exists")

    # Upload the file, renaming it in the process
    client.fput_object(
        bucket_name, destination_file, source_file,
    )
    print(
        source_file, "successfully uploaded as object",
        destination_file, "to bucket", bucket_name,
    )
