import requests
class HttpCli:
    """http client using post request to submit result to server"""
    def __init__(self, url, token=None):
        self.url = url
        self.token = token


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