from src.ucs_alg_node import AlgNode, Alg, AlgResult, AlgSubmitter, AlgNodeWeb
import time


class MyAlg(Alg):
    def __init__(self, mode, sources, model, id):
        super().__init__(mode, model)
        self.name = 'my_alg'
        self.sources = sources
        self.id = id

    def infer_stream(self):
        for i in range(100):
            time.sleep(0.1)
            yield AlgResult(0, 0, 1, "stub result")


def main():
    cfg = {
        'id': 'node',
        'name': 'alg_name',
        'mode': 'stream',
        'max_task': 10,
        'model_dir': './model',  # could be file path or url or model name
        'alg_id': 'alg_id123', # only effective in batch mode
        'web_port':9996
    }

    task = {
        'id': 'task_id123',
        'sources': ['rtsp://localhost:9111/123',
                    'mqx://localhost:8011/1123'],
    }

    alg_cfg = {
        # only effective in stream mode
        'alg_id': 'alg_id123',
        # only effective in stream mode
        'model': 'model_v1.pth',  # could be file path or url or model name
    }

    out_cfg = {
        'dest': 'mqtt://localhost:2799',
        'mode': 'mqtt',
        'username': 'ucs-dev',
        'passwd': 'M*12@va33',
        'topic': 'alg'
    }

    alg = MyAlg(cfg['mode'], task['sources'], alg_cfg['model'], alg_cfg['alg_id'])

    submitter = AlgSubmitter(
        dest=out_cfg['dest'],
        mode=out_cfg['mode'],
        username=out_cfg['username'],
        passwd=out_cfg['passwd'],
        topic=out_cfg['topic']  # if in db mode, can be omitted
    )

    node_cfg = {
        'id': cfg['id'],
        'name': cfg['name'],
        'model_dir': cfg['model_dir'],  # could be file path or url or model name
        'max_task': cfg['max_task'], # only effective in batch mode
        'mode': cfg['mode'],
        'task': task,
        'alg': alg,
        'out': submitter
    }

    node = AlgNode(max_task=10, cfg=node_cfg, task=task)
    node_web_api = AlgNodeWeb(cfg['web_port'], node)

    # node_web_api.run()
    # node.start()
    node_web_api.run()

    print('start node')
    while True:
        time.sleep(5)
        # node.stop()
        # print('stop node, exit')
        # break

if __name__ == '__main__':
    main()
