from src.ucs_alg_node.cli import *

def test_mqtt_cli():
    mqtt_cli = MqttCli({

    })

    def on_connect():
        print('connected to EMQX')
    mqtt_cli.on_connect = on_connect


    mqtt_cli.subscribe('ucs/alg/res')
    mqtt_cli.publish('ucs/alg/res', {
        'status': 'ok',
        'msg': 'connected'
    })

def test_redis_cli():
    redis_cli = RedisCli({
        'host':'localhost',
        'port':6379,
        'password':'123456'
    })
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
        'localhost',
         '9090',
        'pubilc',#这里好像只能起bucket名字，不能用文件夹
         'admin',
        'admin1234'
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
    # test_mqtt_cli()
    # test_redis_cli()
    # test_mqtt_cli()

    test_minio_cli()