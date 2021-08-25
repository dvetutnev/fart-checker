import gas_sensor
import serial

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
          location: 1-3.2

        - model: ZE03-CO
          location: 1-3.3.2
    """
    with patch("gas_sensor.ZE03") as ZE03Class:
        sensor1, sensor2 = Mock(gas_sensor.ZE03), Mock(gas_sensor.ZE03)
        ZE03Class.side_effect = [sensor1, sensor2]

        _, result = gas_sensor.loadConfig(config)

        assert result[0].sensor == sensor1
        assert result[1].sensor == sensor2