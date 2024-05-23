from src.ucs_alg_node.alg_node import AlgNode

config = {
    'port_web': '9901',
    'alg_model': 'model_v1.pth',
    'subscribe': 'mqtt://11,11,11',
    'submit': 'https://local',

    # auth for subscription & output
    'token_subscribe': '',
    'token_submit': '',
}

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
    node = AlgNode(port=9901, max_task=10, config=config)

    node.run()

if __name__ == '__main__':
    main()