import json
import time

from src.ucs_alg_node.cli import RedisCli

host = '62.234.16.239'
port = 6379
db = 'ucs-alg'
bucket = 'ucs-alg'
fname = 'vid_tmp.mp4'
task_id = 'test_id'

task = {
    'id': task_id,
    'ts': time.time_ns(),
    'source' : [''],
    'result': {
        'status': 'ok',
        'msg': {
            'value': [1,2,3,4],
            'descp': 'test result'
        }
    }
}

cli = RedisCli(host, port, db, passwd='123456')

cli.connect()
time.sleep(2)
print('db counts', cli.count())
for i in range(10):
    task_id = 'test_id_%d' % i
    task['result']['msg']['value'] = [i, i+1, i+2, i+3]
    tic = time.time_ns()
    cli.put(task_id, json.dumps(task))
    toc = time.time_ns()
    print('write cost %d'  %(toc-tic))
    tic = time.time_ns()
    task_db = cli.get(task_id)
    toc = time.time_ns()
    print(json.loads(task_db))
    print('read cost %d'  %(toc-tic))
