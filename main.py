#!/usr/bin/env python

# Project FartCHECKER
# Dmitriy Vetutnev, 2021


import aserial
import gas_sensor

import asyncio
import argparse

import influxdb_client


def main():
    parser = argparse.ArgumentParser(description='Project FartCHECKER')
    parser.add_argument("--config", metavar="config", required=True, help="Path to config file")
    args = parser.parse_args()

    file = open(args.config, "r")
    influxdb, sensors = gas_sensor.loadConfig(file)

    client = influxdb_client.InfluxDBClient(url=influxdb.url, token=influxdb.token, org=influxdb.org)
    write_api = client.write_api(write_options=influxdb_client.client.write_api.SYNCHRONOUS)

    def send2influxdb(measure: gas_sensor.Measure):
        point = influxdb_client.Point("air")\
            .tag("location", "MOGES,30")\
            .field(measure.name, measure.value)
        write_api.write(influxdb.bucket, influxdb.org, point)

    port = aserial.ASerial("/dev/ttyUSB0", 9600)
    sensor = gas_sensor.ZE03(gas_sensor.Gas.CO)

    asyncio.run(gas_sensor.readSensor(port, sensor, send2influxdb))


if __name__ == "__main__":
    main()