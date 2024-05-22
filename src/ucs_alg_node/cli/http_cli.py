import requests


def http_get(url, params, headers=None):
    """stateless http get request"""
    if len(params) > 0:
        url += '?'
        first = True
        for k, v in params.items():
            if first:
                url += '%s=%s' % (k, v)
                first = False
            else:
                url += '&%s=%s' % (k, v)

    return requests.get(url, headers=headers).json()


def http_post(url, body, headers=None):
    """stateless http get request"""
    return requests.post(url, data=body, headers=headers).json()


def http_get_file(url, params, headers=None, output_path=None):
    """get method to download large file"""
    if not output_path:
        return -1

    res = http_get(url, params, headers=headers)
    if res['status'] == 'ok':
        file_name = res['data'].split('.')[-2]
        file_ext = res['data'].split('.')[-1]
        with open(output_path+'/'+file_name + '.' + file_ext, 'wb') as f:
            f.write(res['data'])
        return 0


class HttpCli:
    """a http client with default urls to fetch and submit alg results"""
    def __init__(self, host, path=None, token=None):
        if not path:
            # default alg api root
            path = "/api/alg"
        self.url = host + path
        self.token = token

    def fetch_token(self, username, passwd):
        """fetch token from server"""
        res = http_post(self.url + '/auth', {'username': username, 'password': passwd})
        if res['status'] == 'ok':
            self.token = res['msg']['token']
            return 0
        else:
            self.token = None
            return -1

    def submit(self, tid, result):
        """alg result submission"""
        if not self.token:
            return None

        return http_post(self.url + '/result/submit', {'tid': tid, 'result': result}, headers={'Authorization': self.token})

    def fetch_next_task(self, alg_id):
        """fetch next task"""
        return http_get(self.url + '/task/next', {'alg_id':alg_id}, headers={'Authorization': self.token})

    def fetch_task(self, task_id):
        """ fetch task by task_id
        a task can be either pending or with result
        """
        if not self.token:
            return None

        # put token in header
        return http_get(self.url + '/task', params={'task_id':task_id}, headers={'Authorization': self.token})