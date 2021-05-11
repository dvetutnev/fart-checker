#!/usr/bin/env python

# Project FartCHECKER
# Dmitriy Vetutnev, 2021


import serial
from uart import Receiver
from time import localtime, asctime


def main():
    port = serial.Serial("/dev/ttyUSB0")
    while True:
        rx = Receiver()

        packet = port.read(9)
        print(packet)

        rx.put(packet)
        data = rx.get_data()

        concentration = (data[1] * 256) + data[2]
        ts = asctime(localtime())
        print("%s %s ppm" % (ts, concentration))


if __name__ == "__main__":
    main()