from flask import Flask, request, jsonify
import os
import psutil

from . import AlgSubmitter
from .alg_node import AlgNode
from .alg import Alg
from .alg_task import AlgTask
from .alg_result import AlgResult

from .cli import HttpCli


class AlgNodeWeb:
    def __init__(self, port=9001, alg_node=None):
        self.app = Flask(__name__)

        self.node = alg_node

        # 接口声明
        self.api_root = '/api/v1/alg' # v1为版本，alg为根路径

        self.app.add_url_rule(self.api_root+'/about', 'about', self.about, methods=['GET']) # 获取系统负载
        self.app.add_url_rule(self.api_root+'/node/stat', 'node_stat', self.get_node_stat, methods=['GET']) # 获取系统负载
        self.app.add_url_rule(self.api_root + '/alg/info', 'alg_info', self.get_alg_info, methods=['GET']) # 获取算法信息
        self.app.add_url_rule(self.api_root + '/task/info', 'task_info', self.get_task_info, methods=['GET']) # 获取算法信息

        self.app.add_url_rule(self.api_root + '/model/upload', 'upload_model', self.upload_model, methods=['POST']) # 上传模型
        self.app.add_url_rule(self.api_root + '/model/delete', 'delete_model', self.delete_model, methods=['POST']) # 删除模型
        self.app.add_url_rule(self.api_root + '/model/all', 'get_model_list', self.get_model_list, methods=['GET']) # 获取模型列表

        self.app.add_url_rule(self.api_root + '/task/skip', 'alg_skip', self.skip_task, methods=['POST']) # 跳过当前任务
        self.app.add_url_rule(self.api_root + '/reload', 'reload', self.reload, methods=['POST']) # 重置算法

        self.app.add_url_rule(self.api_root + '/cfg/sources', 'alg_cfg_sources', self.config_sources, methods=['POST']) #设置数据源
        self.app.add_url_rule(self.api_root + '/cfg/model', 'alg_cfg_model', self.config_model, methods=['POST']) # 设置模型
        self.app.add_url_rule(self.api_root + '/cfg/out', 'out_cfg', self.config_out, methods=['POST']) # 配置输出

        self.app.add_url_rule(self.api_root + '/task/submit', 'submit_task', self.submit_task, methods=['POST']) # 提交任务

        self.port = port

    def run(self):
        self.app.run(host='localhost', port=self.port)

    def about(self):
        return jsonify(
            {
                'code':'ok',
                'msg': 'UCS Alg node 0.1.2'
            }
        )
    def get_alg_info(self):
        """get algorithm info"""
        return {
            'name': self.node.name,
            'alg_id': self.node.id,
            'sources': self.node.alg.sources,
            'dest': self.node.submitter.dest
        }

    def get_task_info(self):
        return self.node.task

    def get_node_stat(self):
        """get system load, cpu, gpu, memeory occupancy"""
        mem_usage = psutil.virtual_memory()
        return {
            'code': 'ok',
            'msg': {
                # 'sysload': os.getloadavg(), # win32 not supported
                'cpu': psutil.cpu_percent(),
                'gpu': 0,
                'mem': mem_usage.percent,
            }
        }

    def break_alg(self):
        """break current alg task and try the next task"""
        self.node.alg.stop()


    def upload_model(self, url):
        """TODO: upload model file"""
        file = request.files['file']
        model_path = os.path.join(self.node.model_dir, file.filename)
        file.save(model_path)
        pass

    def delete_model(self, model_name):
        model_path = os.path.join(self.node.model_dir, model_name)
        if os.path.exists(model_path):
            os.remove(model_path)
            return jsonify({
                'code': 'ok',
                'msg': 'deleted'
            })
        else:
            return jsonify({
                'code': 'err',
                'msg': 'model not found'
            })

    def get_model_list(self):
        model_dir = self.node.model_dir
        models = []
        for root, dirs, files in os.walk(model_dir):
            for f in files:
                if f.endswith('.pth') or f.endswith('.pt') or f.endswith('.onnx') or f.endswith('.pb') or f.endswith('.h5'):
                    models.append({
                        'name': f,
                        'path': os.path.join(root, f)
                    })
            return models

    def skip_task(self):
        self.node.skip()
        return jsonify({
            'code': 'ok',
            'msg': 'task skipped'
        })

    def reload(self):
        """reload algorithm"""
        if self.node:
            self.node.reload()
            return jsonify({
                'code': 'ok',
                'msg': 'reloading'
            })
        else:
            return jsonify({
                'code': 'err',
                'msg': 'no alg'
            })

    def config_model(self, model_name):
        """config model"""
        has_model = False
        model_list = self.get_model_list()
        for model in model_list:
            if model['name'] == model_name:
                has_model = True
                break

        if has_model:
            self.node.alg.model = model_name
            self.reload()
            return jsonify({
                'code': 'ok',
                'msg': 'model configured'
            })
        else:
            return jsonify({
                'code': 'err',
                'msg': 'model not found'
            })

    def config_sources(self, sources):
        """config sources"""
        self.node.alg.sources = sources
        self.reload()
        return jsonify({
            'code': 'ok',
            'msg': 'sources configured'
        })

    def config_out(self, out_cfg):
        """config output"""
        self.node.alg_submitter = AlgSubmitter(
            dest=out_cfg['dest'],
            mode=out_cfg['mode'],
            username=out_cfg['username'],
            passwd=out_cfg['passwd'],
            topic=out_cfg['topic']  # if in db mode, can be omitted
        )
        return jsonify({
            'code': 'ok',
            'msg': 'output configured'
        })

    def submit_task(self):
        """submit task to node
        """
        # get algtask from request
        alg_task = AlgTask(
            id=request.json['id'],
            ts=request.json['ts'],
            sources=request.json['sources'],
            meta=request.json['meta']
        )
        res = self.node.submit(alg_task)

        if res >= 0:
            return {
                'code': 'ok',
                'msg': ''
            }
        else:
            return {
                'code': 'err',
                'msg': 'submit task failed, code:%d' % res
            }