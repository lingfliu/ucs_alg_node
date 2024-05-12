from alg_node import AlgNode
from alg import Alg

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
    node = AlgNode()

    alg = Alg(mode='stream', sources=['rtsp://localhost:9111/123', 'mqx://localhost:8011//1123'])
    alg.load_model()
    node.set_alg(alg)

    node.reg_subscribe(config['subscribe'])
    node.reg_submit(config['submit'])

    node.start_service_web()
    node.start()

if __name__ == '__main__':
    main()