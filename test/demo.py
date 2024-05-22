from src.ucs_alg_node import *


def main():
    config = {
        'name':'alg_name',
        'sources': ['rtsp://localhost:9111/123',
                    'mqx://localhost:8011//1123'],
        'model': 'model_v1.pth',
        'port':10799,
        'max_task': 10,
        'output_cfg': {
            'dest': 'mqtt://localhost:2799',
            'mode': 'mq',
            'username': 'ucs-dev',
            'passwd': 'M*12@va33',
            'topic': 'alg'
        }
    }
    node = AlgNode(max_task=10, cfg=config)
    # node_web_api = AlgNodeWeb(config['port'], node)

    # node_web_api.run()
    node.run()

if __name__ == '__main__':
    main()