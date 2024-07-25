import json
import time

from flask import Flask, request, jsonify
import os
import psutil

from . import AlgSubmitter
from .alg_node import AlgNode
from .alg import Alg
from .alg_task import AlgTask
from .alg_result import AlgResult

from .cli import HttpCli, MinioCli

#
# minio_host = '62.234.16.239'
# minio_port = 9090
# minio_bucket = 'ucs-alg'
# minio_username = 'admin'
# minio_passwd = 'admin1234'
#
# minioCli = MinioCli(minio_host, minio_port, minio_bucket, minio_username, minio_passwd)

class AlgNodeWeb:
    def __init__(self, port=9001, alg_node=None):
        self.app = Flask(__name__)

        self.node = alg_node
        self.port = port

        # 接口声明
        self.api_root = '/api/v1/algnode' # v1为版本，alg为根路径

        self.app.add_url_rule(self.api_root+'/about', 'node_about', self.about, methods=['GET']) # 获取系统信息
        self.app.add_url_rule(self.api_root+'/stat', 'node_stat', self.get_node_stat, methods=['GET']) # 获取系统负载
        self.app.add_url_rule(self.api_root + '/reload', 'node_reload', self.reload, methods=['POST']) # 重置算法

        self.app.add_url_rule(self.api_root + '/alg/info', 'alg_info', self.get_alg_info, methods=['GET']) # 获取算法信息

        self.app.add_url_rule(self.api_root + '/model/all', 'get_model_list', self.get_model_list, methods=['GET']) # 获取模型列表
        self.app.add_url_rule(self.api_root + '/model/upload', 'upload_model', self.upload_model, methods=['POST']) # 上传模型
        self.app.add_url_rule(self.api_root + '/model/delete', 'delete_model', self.delete_model, methods=['POST']) # 删除模型

        self.app.add_url_rule(self.api_root + '/task/info', 'task_info', self.get_task_info, methods=['GET']) # 获取当前任务信息
        self.app.add_url_rule(self.api_root + '/task/skip', 'task_skip', self.skip, methods=['POST']) # 跳过当前任务
        self.app.add_url_rule(self.api_root + '/task/submit', 'task_submit', self.submit_task, methods=['POST']) # 提交任务
        self.app.add_url_rule(self.api_root + '/task/all', 'task_list', self.get_task_list, methods=['GET']) # 提交任务

        self.app.add_url_rule(self.api_root + '/config/sources', 'alg_cfg_sources', self.config_sources, methods=['POST']) #设置数据源
        self.app.add_url_rule(self.api_root + '/config/model', 'alg_cfg_model', self.config_model, methods=['POST']) # 设置模型
        # self.app.add_url_rule(self.api_root + '/config/dest', 'dest_cfg', self.config_dest, methods=['POST']) # TODO: 配置输出

    def run(self):
        self.app.run(host='0.0.0.0', port=self.port)

    def about(self):
        return {
                'code':'ok',
                'msg': 'UCS Alg node 0.1.3'
            }

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

    def reload(self):
        """reload algorithm"""
        if self.node:
            self.node.reload()
            return {
                'code': 'ok',
                'msg': 'reloading'
            }
        else:
            return {
                'code': 'err',
                'msg': 'no alg'
            }


    def get_alg_info(self):
        """get algorithm info"""
        return {
            'code': 'ok',
            'msg': {
                'name': self.node.name,
                'alg_id': self.node.id,
                'sources': self.node.alg.sources,
                'out': self.node.submitter.dest,
                'model': self.node.alg.model
            }
        }

    def get_task_info(self):
        return self.node.task

    def skip(self):
        """break current alg task and turn  the next task"""
        self.node.skip()
        return self.get_task_list()

    def upload_model(self):
        """upload multipart file"""
        fobj = request.files.get('file')
        fname = request.form['fname']
        fpath = os.path.join(self.node.model_dir, fobj.filename)
        if os.path.exists(fpath):
            return {
                'code': 'err',
                'msg': 'model already exists'
            }
        else:
            fobj.save(fpath)
            return {
                'code': 'ok',
                'msg': {
                    'model': fobj.filename,
                }
            }

        # TODO: download model from minio
        # ret = minioCli.upload(fname, fobj)
        # if ret > 0:
        #     return {
        #         'code': 'ok',
        #         'msg': {
        #             'fname': fname,
        #         }
        #     }
        # else:
        #     return {
        #         'code': 'err',
        #         'msg': 'upload failed'
        #     }

    def delete_model(self):
        model_name = request.get_json()['model']
        model_path = os.path.join(self.node.model_dir, model_name)
        if os.path.exists(model_path):
            os.remove(model_path)
            return {
                'code': 'ok',
                'msg':
                    {
                        'model': model_name
                    }
            }
        else:
            return {
                'code': 'err',
                'msg': 'model not found'
            }


    def skip_task(self):
        self.node.skip()
        return {
            'code': 'ok',
            'msg': 'task skipped'
        }

    def reload(self):
        """reload algorithm"""
        if self.node:
            self.node.reload()
            return {
                'code': 'ok',
                'msg': 'reloading'
            }
        else:
            return {
                'code': 'err',
                'msg': 'no alg'
            }

    def _get_model_list(self):
        model_dir = self.node.model_dir
        models = []
        for root, dirs, files in os.walk(model_dir):
            for f in files:
                if f.endswith('.pth') or f.endswith('.pt') or f.endswith('.onnx') or f.endswith('.pb') or f.endswith(
                        '.h5'):
                    models.append({
                        'name': f,
                        'path': os.path.join(root, f)
                    })

    def get_model_list(self):
        models = self._get_model_list()
        return {
            'code':'ok',
            'msg':models
        }

    def config_model(self):
        """config model"""
        model_name = request.get_json()['model']
        has_model = False
        model_list = self._get_model_list()
        for model in model_list:
            if model['name'] == model_name:
                has_model = True
                break

        if has_model:
            self.node.alg.model = model_name
            return {
                'code': 'ok',
                'msg': {
                    'model': model_name
                }
            }
        else:
            return {
                'code': 'err',
                'msg': 'model not found'
            }

    def config_sources(self, sources):
        """config sources"""
        self.node.alg.sources = sources
        return {
            'code': 'ok',
            'msg': {
                'sources': sources
            }
        }

    def config_out(self, out_cfg):
        """config output"""
        self.node.alg_submitter.stop()
        self.node.alg_submitter = AlgSubmitter(
            dest=out_cfg['dest'],
            mode=out_cfg['mode'],
            username=out_cfg['username'],
            passwd=out_cfg['passwd'],
            topic=out_cfg['topic']  # if in db mode, can be omitted
        )
        return {
            'code': 'ok',
            'msg': {
                'dest': out_cfg['dest'],
                'mode': out_cfg['mode'],
            }
        }

    def submit_task(self):
        """submit task to node
        """
        # get algtask from request
        task = AlgTask(
            id=request.json['id'],
            ts=request.json['ts'],
            sources=request.json['sources'],
            meta=request.json['meta'] if 'meta' in request.json else None
        )
        print('new task sbumitted at', time.time_ns(), 'task queue size', len(self.node.task_list))
        ret = self.node.submit_task(task)

        if ret >= 0:
            return {
                'code': 'ok',
                'msg': {
                    'task_id': task.id,
                    'task_ts': task.ts,
                    'sources': task.sources,
                    'meta': task.meta
                }
            }
        else:
            return {
                'code': 'err',
                'msg': 'submit task failed, code:%d' % ret
            }

    def get_task_list(self):
        tasks = []
        for t in self.node.task_list:
            tasks.append({
                'id': t.id,
                'ts': t.ts,
                'sources': t.sources,
                'meta': t.meta
            })
        return {
            'code': 'ok',
            'msg':tasks
        }