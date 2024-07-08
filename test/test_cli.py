from src.ucs_alg_node.cli import *
import json
import time
import tornado.ioloop
def test_mqtt_cli():
    mqtt_cli = MqttCli(
        # host='localhost',
        host='62.234.16.239',
        port=1883,
        username='admin',  # 默认账号
        passwd='public',  # 默认密码
        topics='/ucs/alg'
    )

    def on_connect():
        print('connected to EMQX')

    mqtt_cli.on_connect = on_connect()
    # 连接到 MQTT 代理
    mqtt_cli.connect()
    # 新建特定话题
    topic = "ucs/alg/res"
    # 订阅话题
    mqtt_cli.subscribe()
    # 监听订阅的消息发布
    # try:
    #     # 循环以保持连接并处理消息
    #     while True:
    #         # 在此处添加你的其他逻辑
    #         time.sleep(1)  # 这里可以添加其他逻辑，同时保持程序在运行
    # except KeyboardInterrupt:
    #     print("Interrupted")

    # 发布默认话题topics
    mqtt_cli.publish(json.dumps({
        "status": "ok",
        "msg": "connected"}))
    # # 发布特定话题
    mqtt_cli.publish_to(topic, json.dumps({
        "status": "ok",
        "msg": "connected"}))

def test_redis_cli():
    redis_cli = RedisCli(
        # host='localhost',
        host='62.234.16.239',
        port=6379,
        db=0,  # 默认数据库索引
        username=None,  # 如果没有用户名认证，则留空
        passwd='123456'
    )
    redis_cli.connect()

    redis_cli.set('test', 'test')
    redis_cli.get('test')


def test_mq_cli():
    def on_message(msg):
        print('received: ', msg)

    mq_cli = MqCli(
        # host='localhost',
        host='62.234.16.239',
        port=4150,
        topic='test_topic1',
        channel='test',
        username=None,  # 如果没有用户名认证，则留空
        passwd=None,
        on_message=on_message
    )
    # 订阅特殊话题
    print("订阅特殊话题")
    mq_cli.subscribe('test_topic6')

    # mq_cli.publish({
    #     'status': 'ok',
    #     'err': None
    # })
    def pub_message():
        # current_time = time.strftime('%H:%M:%S').encode('utf-8')
        current_time = {
            'status': 'ok',
            'err': None
        }
        mq_cli.publish(current_time)
    # 设置定时器，每隔 1000 毫秒（1 秒）发布一次消息
    tornado.ioloop.PeriodicCallback(pub_message, 1000).start()

    # 连接到 NSQ 并订阅主题
    mq_cli.connect()


def test_minio_cli():
    """test for minio upload, download, query, count"""
    minio_cli = MinioCli(
        # host='localhost',
        host='62.234.16.239',
        port='9090',
        bucket='public',  # 这里好像只能起bucket名字，不能用文件夹
        username='admin',
        passwd='admin1234'
    )

    fobj_list = minio_cli.query_all()
    # print(fobj_list)
    for fobj in fobj_list:
        # todo: download all fobj_list
        # minio_cli.download()
        pass

    # The file to upload, change this path if needed 本地文件上传
    # source_file = r"D:\py_program\ucs_alg_node\requirements.txt"
    # destination_file = "requirements.txt"
    # minio_cli.upload(destination_file, source_file)

    # The file to download, change this path if needed 文件下载
    source_file = r"D:\py_program\ucs_alg_node\requirements01.txt"
    destination_file = "requirements.txt"
    minio_cli.download(destination_file, source_file)


if __name__ == '__main__':
    # test_mqtt_cli()
    # test_redis_cli()
    test_mq_cli()

    # test_minio_cli()
