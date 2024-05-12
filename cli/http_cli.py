import requests
class HttpCli:
    """http client using post request to submit result to server"""
    def __init__(self, url, token=None):
        self.url = url
        self.token = token


    def get(self, url, params, headers=None):
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

    def post(self, url, body, headers=None):
        return requests.post(url, data=body, headers=headers).json()

    def _get(self, path, headers=None):
        if not self.token:
            return None

        url = self.url + path
        response = requests.get(url, headers=headers)
        return response.json()

    def _post(self, path, data, headers=None):
        if not self.token:
            return None

        url = self.url + path
        response = requests.post(url, json=data, headers=headers)
        return response.json()

    def submit(self, tid, result):
        """ result submission"""
        if not self.token:
            return None

        return self._post('/submit', {'tid': tid, 'result': result}, headers={'Authorization': self.token})

    def fetch(self):
        """ fetch result by tid"""
        if not self.token:
            return None

        # put token in header
        return self._get('/fetch/', headers={'Authorization': self.token})