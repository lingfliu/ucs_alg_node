from web_srv import WebSrv

from alg import Alg

class AlgNode:
    def __init__(self, port=9001, max_task=10, alg_config=None):
        if alg_config:
            self.alg = Alg({
                'mode': alg_config['mode'],
                'sources': alg_config['sources'],
                'model': alg_config['model']
            })
        else:
            self.alg = None
        self.res_buff = []
        self.task_queue = []
        self.task_queue_max = max_task

        self.http_service = WebSrv(port, alg_node=self)

    def set_alg(self, alg):
        self.alg = alg

    def reload(self):
        if self.alg:
            self.alg.reload()

    def start(self):
        if self.alg:
            if self.alg.mode == 'stream':
                for res in self.alg.infer():
                    self.submit(res)

    def infer(self, alg_task):
        '''synchronous infer'''
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

        self.mq.submit(res)

