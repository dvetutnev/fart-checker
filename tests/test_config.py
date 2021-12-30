import gas_sensor
from gas_sensor import Gas

from serial.tools.list_ports_common import ListPortInfo

import pytest
from unittest.mock import patch, Mock, call


def test_config_influx():
    config = """
influxdb:
    url: https://influxdb.kysa.me/
    org: kysa.me
    bucket: FartCHECKER
    token: t0ken

sensors:
    - model: ZE03-H2S
      location: 1-3.2.99.999
"""
    result, _ = gas_sensor.loadConfig(config)

    assert isinstance(result, gas_sensor.InfluxConfig)

    assert result.url == "https://influxdb.kysa.me/"
    assert result.org == "kysa.me"
    assert result.bucket == "FartCHECKER"
    assert result.token == "t0ken"


def test_config_influx_missing():
    config = """
sensors:
    - model: ZE03-H2S
      location: 1-3.2.99.999
"""
    with pytest.raises(Exception) as ex:
        result, _ = gas_sensor.loadConfig(config)
    print(ex)


def test_config_influx_missing_field():
    config = """
influxdb:
    url: https://influxdb.kysa.me/
    org: kysa.me
    bucket: FartCHECKER

sensors:
    - model: ZE03-H2S
      location: 1-3.2.99.999
"""
    with pytest.raises(Exception) as ex:
        result, _ = gas_sensor.loadConfig(config)
    print(ex)


def test_config_sensors():
    config = """
influxdb:
    url: https://influxdb.kysa.me/
    org: kysa.me
    bucket: FartCHECKER
    token: t0ken
    
sensors:
    - model: ZE03-H2S
      location: 1-3.2.77

    - model: ZE03-CO
      location: 1-3.3.2.55
"""
    with patch("gas_sensor.ZE03") as ZE03Class,\
         patch("serial.tools.list_ports.comports") as comports:

        sensor1, sensor2 = Mock(gas_sensor.ZE03), Mock(gas_sensor.ZE03)
        ZE03Class.side_effect = [sensor1, sensor2]

        port1 = ListPortInfo("/dev/usb97")
        port1.location = "1-3.3.2.55"
        port2 = ListPortInfo("/dev/usb98")
        port2.location = "1-3.2.77"
        comports.return_value = [port1, port2]

        _, result = gas_sensor.loadConfig(config)

        assert result[0].sensor == sensor1
        assert result[1].sensor == sensor2

        assert ZE03Class.call_args_list == [call(Gas.H2S), call(Gas.CO)]

        assert result[0].device == "/dev/usb98"
        assert result[1].device == "/dev/usb97"


def test_config_sensors_skip_not_found():
    config = """
influxdb:
    url: https://influxdb.kysa.me/
    org: kysa.me
    bucket: FartCHECKER
    token: t0ken

sensors:
    - model: ZE03-H2S
      location: 1-3.2.77

    - model: ZE03-CO
      location: 1-3.3.2.54
"""
    with patch("gas_sensor.ZE03") as ZE03Class, \
         patch("serial.tools.list_ports.comports") as comports:
        sensor1, sensor2 = Mock(gas_sensor.ZE03), Mock(gas_sensor.ZE03)
        ZE03Class.side_effect = [sensor1, sensor2]

        port1 = ListPortInfo("/dev/usb97")
        port1.location = "1-3.3.2.55"
        port2 = ListPortInfo("/dev/usb98")
        port2.location = "1-3.2.77"
        comports.return_value = [port1, port2]

        _, result = gas_sensor.loadConfig(config)

        assert len(result) == 1


def test_config_without_sensors():
    config = """
influxdb:
    url: https://influxdb.kysa.me/
    org: kysa.me
    bucket: FartCHECKER
    token: t0ken
"""
    with pytest.raises(Exception) as ex:
        gas_sensor.loadConfig(config)
    print(ex)


def test_config_sensors_missing_model():
    config = """
influxdb:
    url: https://influxdb.kysa.me/
    org: kysa.me
    bucket: FartCHECKER
    token: t0ken
sensors:
    - location: 1-3.88
"""
    with pytest.raises(Exception) as ex:
        gas_sensor.loadConfig(config)
    print(ex)


def test_config_sensors_missing_location():
    config = """
influxdb:
    url: https://influxdb.kysa.me/
    org: kysa.me
    bucket: FartCHECKER
    token: t0ken
sensors:
    - model: ZE03-SO2
    """
    with pytest.raises(Exception) as ex:
        gas_sensor.loadConfig(config)
    print(ex)
