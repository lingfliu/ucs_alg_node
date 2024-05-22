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
    redis_cli = RedisCli({})

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
    minio_cli = MinioCli({
        'host': 'localhost:9000',
        'bucket':'ucs/alg/res',
        'username': 'admin',
        'passwd': 'admin123'
    })

    fobj_list = minio_cli.query_all()
    for fobj in fobj_list:
        # todo: download all fobj_list
        # minio_cli.download()
        pass

if __name__ == '__main__':
    test_mqtt_cli()
    test_redis_cli()
    test_mqtt_cli()
    test_minio_cli()