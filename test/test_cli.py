import json
import time

from src.ucs_alg_node.cli import MqttCli, RedisCli, MqCli, MinioCli


host = '62.234.16.239'

def test_mqtt_cli():
    default_topic = 'ucs/alg'
    mqtt_cli = MqttCli(
        host = host,
        port = 1883,
        username = 'admin',#默认账号
        passwd = 'public',#默认密码
        topics = [default_topic],
        id='node112'
    )

    mqtt_cli.connect()

    time.sleep(5)
    print('runs here')
    for i in range(10):
        msg = {
            'status': 'ok',
            'msg': {
                'value': [0,1,2,3],
                'descp': 'test result',
                'task_ts': time.time_ns()/1000,
            }
        }
        mqtt_cli.publish('ucs/alg', json.dumps(msg))

    while True:
        time.sleep(1)





def test_redis_cli():
    redis_cli = RedisCli(
        host='localhost',
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

    mq_cli = MqCli({
        'host': 'localhost:9092',
        'topic': 'test',
        'channel': 'test',
        'on_message': on_message
        })

    mq_cli.connect()
    mq_cli.publish({
        'status': 'ok',
        'err': None
    })


def test_minio_cli():
    """test for minio upload, download, query, count"""
    minio_cli = MinioCli(
        host='localhost',
        port='9090',
        bucket='pubilc',#这里好像只能起bucket名字，不能用文件夹
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
    # source_file = r"D:\py program\ucs_alg_node\requirements.txt"
    #
    # destination_file = "requirements05.txt"
    # minio_cli.upload(destination_file, source_file)
    # The file to download, change this path if needed 文件下载
    source_file = r"D:\py program\ucs_alg_node\requirements05.txt"
    destination_file = "requirements01.txt"
    minio_cli.download(destination_file,source_file)



if __name__ == '__main__':
    test_mqtt_cli()
    # test_redis_cli()
    # test_mq_cli()
    # test_minio_cli()
