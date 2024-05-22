import utils
from web_srv import WebSrv

from alg import Alg
from alg_submitter import AlgSubmitter

import threading

ALG_STATE_IDLE = 0
ALG_STATE_RUNNING = 1
ALG_STATE_ERROR = 2


class AlgNode:
    def __init__(self, port=9001, max_task=10, config=None):
        if config:
            self.alg = Alg({
                'mode': config['mode'],
                'sources': config['sources'],
                'model': config['model']
            })

            out_cfg = config['output_cfg']
            self.alg_submitter = AlgSubmitter(dest=out_cfg['dest'],
                                              mode= out_cfg['moode'],
                                                username=out_cfg['username'],
                                                passwd=out_cfg['passwd'],
                                                topic=out_cfg['topic'])

            self.alg.load_model()

        else:
            self.alg = None
            self.alg_submitter = None

        self.res_buff = []
        self.task_queue = []
        self.task_queue_max = max_task

        self.web_service = WebSrv(port, alg_node=self)

    def reload(self):
        if self.alg:
            self.alg.reload()

    def run(self):
        """only called for stream mode alg"""
        if self.alg:
            threading.Thread(target=self._run).start()
            return 0
        else:
            return -1

    def _run(self):
        """task loop for stream mode alg"""
        if self.alg.mode == 'stream':
            for res in self.alg.infer():
                self.submit_result(res)

    def infer_batch(self, alg_task):
        """synchronous infer"""
        if self.alg.mode == 'batch':
            res = self.alg.infer_batch(alg_task.input)
            # wrap result with task infos
            if res:
                self.submit_result({
                    'tid': alg_task.tid,
                    'task_ts': alg_task.ts,
                    'result_ts': utils.current_time_milli(),
                    'res': res,
                })
                return 0
            else:
                return self.submit_result({
                    'tid': alg_task.tid,
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



