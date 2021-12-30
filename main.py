#!/usr/bin/env python

# Project FartCHECKER
# Dmitriy Vetutnev, 2021


import aserial
import gas_sensor

import asyncio
import argparse

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS


def main():
    parser = argparse.ArgumentParser(description='Project FartCHECKER')
    parser.add_argument("--config", metavar="config", required=True, help="Path to config file")
    args = parser.parse_args()

    file = open(args.config, "r")
    influxdb, sensors = gas_sensor.loadConfig(file)

    client = InfluxDBClient(url=influxdb.url, token=influxdb.token, org=influxdb.org)
    write_api = client.write_api(write_options=SYNCHRONOUS)

    point = Point("air").tag("location", "MOGES,30").field("SO2", 100)
    write_api.write(influxdb.bucket, point)

    print("exit")
    exit(0)

    port = aserial.ASerial("/dev/ttyUSB0", 9600)
    sensor = gas_sensor.ZE03(gas_sensor.Gas.CO)
    def dashBoard(measure): print(measure)

    asyncio.run(gas_sensor.readSensor(port, sensor, dashBoard))


if __name__ == "__main__":
    main()