import cli
from web_srv import WebSrv

from alg import Alg

class AlgNode:
    def __init__(self, port=9001, max_task=10, config=None):
        if config:
            self.alg = Alg({
                'mode': config['mode'],
                'sources': config['sources'],
                'model': config['model']
            })

            result_submit_mode = config['submit'].split('://')[0]
            #todo implement submit cli
            if 'http' in result_submit_mode:
                self.submit_cli = cli.MqCli(config['submit'])
            elif 'mqtt' in result_submit_mode:
                self.submit_cli = cli.MqttCli(config['submit'])
            elif 'kafka' in result_submit_mode:
                self.submit_mode = 'kafka'
            elif 'redis' in result_submit_mode:
                self.submit_mode = 'redis'
            elif 'nsq' in result_submit_mode:
                self.submit_mode = 'nsq'
            else:
                self.submit_cli = None

        else:
            self.alg = None
            self.submit_cli = None

        self.res_buff = []
        self.task_queue = []
        self.task_queue_max = max_task

        self.web_service = WebSrv(port, alg_node=self)

    def set_alg(self, alg):
        self.alg = alg

    def reload(self):
        if self.alg:
            self.alg.reload()

    def start(self):
        """only called for stream mode alg"""
        if self.alg:
            if self.alg.mode == 'stream':
                for res in self.alg.infer():
                    self.submit_result(res)

    def infer(self, alg_task):
        """synchronous infer"""
        if self.alg.mode == 'batch':
            res = self.alg.infer_batch(alg_task.input)
            # wrap result with task infos
            if res:
                self.submit_result({
                    'tid': alg_task.tid,
                    'ts': alg_task.ts,
                    'res': res,
                })
                return 0
            else:
                return self.submit_result({
                    'tid': alg_task.tid,
                    'ts': alg_task.ts,
                    'res': 'failed',
                })
        else:
            return -1

    def submit_result(self, res):
        # todo: config res_buff length
        if len(self.res_buff) > 10:
            # fifo buffer
            self.res_buff.pop(0)
            self.res_buff.append(res)

        if self.submit_mode == 'http':
            self.submit_cli.submit(res)



