import requests
class HttpCli:
    def __init__(self, url):
        self.url = url

    def get(self, path):
        url = self.url + path
        response = requests.get(url)
        return response.json()

    def post(self, path, data):
        url = self.url + path
        response = requests.post(url, json=data)
        return response.json()