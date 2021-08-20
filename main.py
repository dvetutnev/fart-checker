#!/usr/bin/env python

# Project FartCHECKER
# Dmitriy Vetutnev, 2021


import aserial
import gas_sensor
import asyncio


def main():
    print("Project FartCHECKER")

    port = aserial.ASerial("/dev/ttyUSB0", 9600)
    sensor = gas_sensor.ZE03(gas_sensor.Gas.CO)
    def dashBoard(measure): print(measure)

    asyncio.run(gas_sensor.readSensor(port, sensor, dashBoard))


if __name__ == "__main__":
    main()