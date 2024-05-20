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
    """http client using post request to submit result to server"""
    def __init__(self, url, path=None, token=None):
        if not path:
            path = "/api/alg"
        self.url = url + path
        self.token = token

    def submit(self, tid, result):
        """alg result submission"""
        if not self.token:
            return None

        return http_post(self.url + '/result/submit', {'tid': tid, 'result': result}, headers={'Authorization': self.token})

    def fetch(self):
        """ fetch result by tid"""
        if not self.token:
            return None

        # put token in header
        return http_get(self.url + '/result/fetch/', headers={'Authorization': self.token})