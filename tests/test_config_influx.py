import gas_sensor
import pytest


def test_config_influx():
    config = """
    - influxdb:
        url: https://influxdb.kysa.me/
        org: kysa.me
        bucket: FartCHECKER
        token: t0ken
    """
    result, _ = gas_sensor.loadConfig(config)

    assert isinstance(result, gas_sensor.InfluxConfig)

    assert result.url == "https://influxdb.kysa.me/"
    assert result.org == "kysa.me"
    assert result.bucket == "FartCHECKER"
    assert result.token == "t0ken"


def test_config_influx_missing():
    config = """
        url: https://influxdb.kysa.me/
        org: kysa.me
        bucket: FartCHECKER
    """
    with pytest.raises(Exception) as ex:
        result, _ = gas_sensor.loadConfig(config)
    print(ex)


def test_config_influx_missing_field():
    config = """
    - influxdb:
        url: https://influxdb.kysa.me/
        org: kysa.me
        bucket: FartCHECKER
    """
    with pytest.raises(Exception) as ex:
        result, _ = gas_sensor.loadConfig(config)
    print(ex)