"""
InfluxConfig, [PortConfig]
"""


from gas_sensor import Gas

class PortConfig:

    def __init__(self, path, name):
        self._path = path
        self._name = name

    @property
    def path(self):
        return self._path

    @property
    def name(self):
        return self._name


class InfluxConfig:

    def __init__(self, url, org, bucket, token):
        self._url = url
        self._org = org
        self._bucket = bucket
        self._token = token

    @property
    def url(self):
        return self._url

    @property
    def org(self):
        return self._org

    @property
    def bucket(self):
        return self._bucket

    @property
    def token(self):
        return self._token


def loadConfig():
    pass