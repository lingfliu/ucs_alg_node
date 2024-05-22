from src.ucs_alg_node import *
import time


class MyAlg(Alg):
    def __init__(self, mode, sources, model):
        super().__init__(mode, sources, model)

    def infer_stream(self):
        for i in range(10):
            time.sleep(1)
            yield AlgResult(0, 0, 1, "stub result")


def main():
    cfg = {
        'name':'alg_name',
        'sources': ['rtsp://localhost:9111/123',
                    'mqx://localhost:8011//1123'],
        'model': 'model_v1.pth',
        'mode': 'stream',
        'max_task': 10,
        'out': {
            'dest': 'mqtt://localhost:2799',
            'mode': 'mq',
            'username': 'ucs-dev',
            'passwd': 'M*12@va33',
            'topic': 'alg'
        }
    }
    node = AlgNode(max_task=10, cfg=cfg)
    # node_web_api = AlgNodeWeb(config['port'], node)

    # node_web_api.run()
    node.alg = MyAlg(cfg['mode'], cfg['sources'], cfg['model'])
    node.run()


    while True:
        time.sleep(1)
        print('running...')

if __name__ == '__main__':
    main()
