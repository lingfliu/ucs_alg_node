from flask import Flask, request, jsonify
import os
import psutil
from src.ucs_alg_node.alg_node import AlgNode

from src.ucs_alg_node.cli import HttpCli


class WebSrv:
    def __init__(self, port=9001, alg_node=None):
        self.app = Flask(__name__)

        self.alg_node = alg_node

        # 接口声明
        self.app.add_url_rule('api/stat/sysload', 'stat_sysload', self.get_stat_sysload, methods=['GET']) # 获取系统负载
        self.app.add_url_rule('api/stat/alg', 'stat_alg', self.get_stat_alg, methods=['GET']) # 获取算法状态
        self.app.add_url_rule('api/model/upload', 'upload_model', self.upload_model, methods=['POST']) # 上传模型
        self.app.add_url_rule('api/model/delete', 'delete_model', self.delete_model, methods=['POST']) # 删除模型
        self.app.add_url_rule('api/model/all', 'get_model_list', self.get_model_list, methods=['GET']) # 获取模型列表
        self.app.add_url_rule('api/cfg/source', 'cfg_source', self.config_sources, methods=['POST']) # 配置数据源
        self.app.add_url_rule('api/cfg/alg', 'cfg_alg', self.config_alg, methods=['POST']) # 配置算法
        self.app.add_url_rule('api/op/reload', 'reload', self.reload_alg, methods=['POST']) # 重载算法
        self.app.add_url_rule('api/op/task/cleanup', 'task_cleanup', self.task_cleanup, methods=['POST']) # 清理任务

        self.cli = HttpCli()
        self.app.run(host='localhost', port=port)


    def get_stat_sysload(self):
        """get system load, cpu, gpu, memeory occupancy"""
        mem_usage = psutil.virtual_memory()
        return {
            'sysload': os.getloadavg(),
            'cpu': psutil.cpu_percent(),
            'gpu': 0,
            'mem': mem_usage.percent,
        }

    def get_stat_alg(self):
        """get algorithm status"""
        return {
            'code': 'ok',
            'msg': {
                'name': self.alg_node.name,
                'stats': self.alg_node.stats,
                'model': self.alg_node.model,
            }
        }

    def config_sources(self, sources):
        """update sources for inference"""
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
        """config algorithm
        :param config: dict
        {
            'name': 'alg_name',
            'model': 'model_v1.pth',
            'mode': 'stream',
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

    def config_submit(self, submit):
        """config submit address
        :param submit: str
        """
        self.alg_node.reg_submit(submit)
        return {
            'code': 'ok',
            'msg': ''
        }

    def reload_alg(self):
        """reload algorithm"""
        if self.alg_node:
            self.alg_node.reset()
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
        """submit task to server
        :param task: dict
        {
            'task_id': '123',
            'ts': '10229192',
            'data': 'data',
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
