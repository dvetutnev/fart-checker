#!/usr/bin/env python

# Project FartCHECKER
# Dmitriy Vetutnev, 2021


import serial
from uart import Receiver
from time import localtime, asctime


def get_concentration(packet):
    return (packet[1] * 256) + packet[2]


def callback(packet):
    time = asctime(localtime())
    concentration = get_concentration(packet)
    print("%s %s ppm" % (time, concentration))


def main():
    print("Project FartCHECKER")

    port = serial.Serial("/dev/ttyUSB0")
    rx = Receiver(callback)

    while True:
        b = port.read()
        rx.input(b)


if __name__ == "__main__":
    main()