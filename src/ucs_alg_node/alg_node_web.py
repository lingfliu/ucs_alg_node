from flask import Flask, request, jsonify
import os
import psutil
from .alg_node import AlgNode

from .cli import HttpCli


class AlgNodeWeb:
    def __init__(self, port=9001, alg_node=None):
        self.app = Flask(__name__)

        self.node = alg_node

        # 接口声明

        self.app.add_url_rule('api/node/stat', 'node_stat', self.get_node_stat, methods=['GET']) # 获取系统负载

        self.app.add_url_rule('api/alg/info', 'alg_info', self.get_alg_info, methods=['GET']) # 获取算法信息

        self.app.add_url_rule('api/alg/model/upload', 'upload_model', self.upload_model, methods=['POST']) # 上传模型
        self.app.add_url_rule('api/alg/model/delete', 'delete_model', self.delete_model, methods=['POST']) # 删除模型
        self.app.add_url_rule('api/alg/model/all', 'get_model_list', self.get_model_list, methods=['GET']) # 获取模型列表
        self.app.add_url_rule('api/alg/break', 'alg_break', self.break_alg, methods=['POST']) # 清理任务
        self.app.add_url_rule('api/alg/reload', 'reload', self.reload_alg, methods=['POST']) # 重载算法

        self.app.add_url_rule('api/cfg/alg', 'cfg_alg', self.config_alg, methods=['POST']) # 配置算法
        self.app.add_url_rule('api/cfg/node', 'cfg_node', self.config_node, methods=['POST']) # 配置算法

        self.app.add_url_rule('api/task/submit', 'submit_task', self.submit_task, methods=['POST']) # 提交任务

        self.cli = HttpCli()
        self.app.run(host='localhost', port=port)

        self.port = port

    def run(self):
        self.app.run(host='localhost', port=self.port)

    def get_alg_info(self):
        """get algorithm info"""
        return {
            'name': self.node.name,
            'description': self.node.descrip,
            'alg_id': self.node.id,
            'sources': self.node.sources,
            'dest': self.node.dest
        }

    def get_node_stat(self):
        """get system load, cpu, gpu, memeory occupancy"""
        mem_usage = psutil.virtual_memory()
        return {
            'sys': {
                'sysload': os.getloadavg(),
                'cpu': psutil.cpu_percent(),
                'gpu': 0,
                'mem': mem_usage.percent,
            },
            'alg': {
                'task_id': self.node.task_id,
                'task_stat': self.node.task_stat,
            }
        }

    def config_alg(self, cfg):
        self.node.alg.sources = cfg['sources']
        self.node.alg.dest = cfg['dest']
        self.node.alg.model = cfg['model']

    def break_alg(self):
        """break current alg task and try the next task"""
        self.node.alg.stop()

    def reload_alg(self):
        """TODO: test"""
        self.node.alg.reload()

    def config_alg(self, config):
        """config algorithm
        called at initialization
        :param config: dict
        {
            'name': 'alg_name',
            'model': 'model_v1.pth',
            'mode': 'stream',
            'sources': ['rtsp://localhost:9111/123'],
            'dest': ''
        }
        """
        if self.alg_node:
            self.alg_node.reload(config)
        else:
            self.alg_node = AlgNode(config)

        return jsonify({
            'code': 'ok',
            'msg': 'config success'
        })

    def config_node(self, cfg):
        """config submit address
        :param submit: str
        {
            'node_id':'id',
            'node_name':'name',
            'node_desc':'desc'
        }
        """
        self.alg_node.reload(cfg)
        return {
            'code': 'ok',
            'msg': ''
        }

    def reload_alg(self):
        """reload algorithm"""
        if self.alg_node:
            self.alg_node.reload()
        else:
            pass

    def cleanup_task(self):
        """cleanup task"""
        self.alg_node.cleanup()
        return {
            'code': 'ok',
            'msg': ''
        }

    def submit_task(self, task):
        """submit task to node
        :param task: dict
        {
            'task_id': '123',
            'ts': '10229192',
            'data': ['http://202.123.33.25/bfile/123.avi'],
            'meta_data': {
                'meta1':'1',
                'meta2':'2'
            }
        }
        """
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

    def upload_model(self, model_info):
        """upload model file"""
        file = request.files['file']
        model_path = os.path.join(self.alg_node.model_dir, file.filename)
        file.save(model_path)

    def delete_model(self, model_info):
        """upload model file"""
        file = request.files['file']
        model_path = os.path.join(self.alg_node.model_dir, file.filename)
        file.save(model_path)

    def get_model_list(self):
        model_dir = self.alg_node.model_dir
        models = []
        for root, dirs, files in os.walk(model_dir):
            for f in files:
                if f.endswith('.pth'):
                    models.append({
                        'name': f,
                        'path': os.path.join(root, f)
                    })
            return models
