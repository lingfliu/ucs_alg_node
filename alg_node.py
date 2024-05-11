from web_srv import WebSrv

from alg import Alg

class AlgNode:
    def __init__(self, port=9001, max_task=10, alg_config=None):
        if alg_config:
            self.alg = Alg(alg_config)
        else:
            self.alg = None
        self.res_buff = None
        self.task_queue = []
        self.task_queue_max = max_task

        self.http_service = WebSrv(port, alg_node=self)


    def set_alg(self, alg):
        self.alg = alg

    def start(self):
        if self.alg:
            if self.alg.mode == 'stream':
                for res in self.alg.infer():
                    self.submit(res)

    def infer(self, data):
        '''synchronous infer'''
        if self.alg.mode == 'batch':
            res = self.alg.infer_batch(data)
            if res:
                self.submit(res)
                return 0
            else:
                # todo: wrap result with task information
                return res
        else:
            return -1