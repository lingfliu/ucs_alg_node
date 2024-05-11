from flask import Flask, request, jsonify
import os
import psutil
from alg_node import AlgNode

class WebSrv:
    def __init__(self, port=9001, alg_node=None):
        self.app = Flask(__name__)

        self.alg_node = alg_node

        self.app.add_url_rule('api/stat/sysload', 'stat_sysload', self.get_stat_sysload, methods=['GET'])
        self.app.add_url_rule('api/stat/alg', 'stat_alg', self.get_stat_alg, methods=['GET'])
        self.app.add_url_rule('api/cfg/source', 'cfg_source', self.config_sources, methods=['POST'])
        self.app.add_url_rule('api/cfg/alg', 'cfg_alg', self.config_alg, methods=['POST'])
        self.app.add_url_rule('api/op/reload', 'reload', self.reload_alg, methods=['POST'])
        self.app.add_url_rule('api/op/task/cleanup', 'task_cleanup', self.task_cleanup, methods=['POST'])

        self.app.run(host='localhost', port=port)


    def get_stat_sysload(self):
        '''get system load, cpu, gpu, memeory occupancy'''
        mem_usage = psutil.virtual_memory()
        return {
            'sysload': os.getloadavg(),
            'cpu': psutil.cpu_percent(),
            'gpu': 0,
            'mem': mem_usage.percent,
        }

    def get_stat_alg(self):
        '''get algorithm status'''
        return {
            'code': 'ok',
            'msg': {
                'name': self.alg_node.name,
                'stats': 'suspend',
                'model': self.alg_node.model,
            }
        }

    def config_sources(self, sources):
        '''update sources for inference'''
        res = self.alg_node.reg_sources(sources)
        if res >= 0:
            return {
                'code': 'ok',
                'msg': ''
            }
        else:
            return {
                'code': 'err',
                'msg': 'failed, code:%d' % res
            }


    def config_alg(self, config):
        '''config algorithm
        :param config: dict
        {
            'name': 'alg_name',
            'model': 'model_v1.pth',
            'mode': 'stream',
        }
        '''
        if self.alg_node:
            self.alg_node.reload(config)
        else:
            self.alg_node = AlgNode(config)

        return jsonify({
            'code': 'ok',
            'msg': 'config success'
        })

    def config_submit(self, submit):
        '''config submit address
        :param submit: str
        '''
        self.alg_node.reg_submit(submit)
        return {
            'code': 'ok',
            'msg': ''
        }

    def reload_alg(self):
        '''reload algorithm'''
        if self.alg_node:
            self.alg_node.reset()
        else:
            pass

    def cleanup_task(self):
        '''cleanup task'''
        self.alg_node.cleanup()
        return {
            'code': 'ok',
            'msg': ''
        }

    def submit_task(self, task):
        '''submit task to server
        :param task: dict
        {
            'task_id': '123',
            'ts': '10229192',
            'data': 'data',
        }
        '''
        res = self.alg_node.submit(task)
        if res >= 0:
            return {
                'code': 'ok',
                'msg': ''
            }
        else:
            return {
                'code': 'err',
                'msg': 'failed, code:%d' % res
            }