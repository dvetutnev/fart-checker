"""
loadConfig(stream): -> InfluxConfig, [PortConfig]
"""


import gas_sensor
from gas_sensor import Gas

import yaml
import serial.tools.list_ports


class PortConfig:

    def __init__(self, device, sensor):
        self._device = device
        self._sensor = sensor

    @property
    def device(self):
        return self._device

    @property
    def sensor(self):
        return self._sensor


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



def loadInfluxConfig(conf):
    for key in ("url", "org", "bucket", "token"):
        if key not in conf:
            raise Exception("Invalid config, not found 'influxdb: {0}'".format(key))

    return InfluxConfig(conf["url"], conf["org"], conf["bucket"], conf["token"])


def createSensor(model):
    name, gas = model.split("-")
    if name == "ZE03":
        return gas_sensor.ZE03(Gas[gas])
    else:
        raise Exception("Invalid sensor model '{0}'".format(model))


def loadPortConfig(conf):
    for key in ("model", "location"):
        if key not in conf:
            raise Exception("Invalid config, not found 'sensor: {0}'".format(key))

    listPortInfo = serial.tools.list_ports.comports()

    for portInfo in filter(lambda portInfo: portInfo.location == conf["location"], listPortInfo):
        device = portInfo.device
        sensor = createSensor(conf["model"])
        return PortConfig(device, sensor)
    else:
        return None


def loadConfig(source):
    conf = yaml.full_load(source)

    if "influxdb" not in conf:
        raise Exception("Invalid config, not found 'influxdb'")
    influx = loadInfluxConfig(conf["influxdb"])

    if "sensors" not in conf:
        raise Exception("Invalid config, not found 'sensors'")
    ports = []
    for portConf in conf["sensors"]:
        port = loadPortConfig(portConf)
        if port:
            ports.append(port)

    return influx, ports
