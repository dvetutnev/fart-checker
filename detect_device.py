#!/usr/bin/env python


import pyudev
import asyncio
import serial.tools.list_ports


def on_udev_event(monitor):
    while True:
        device = monitor.poll(0)
        if device is None:
            break
        print('{0.action} on {0.sys_name}'.format(device))
        if device.action == 'bind':
            path = '/dev/{0.sys_name}'.format(device)
            location = next(filter(lambda d: d.device == path, serial.tools.list_ports.comports())).location
            print(location)

if __name__ == "__main__":
    print(pyudev.udev_version())

    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by(subsystem='usb-serial')
    monitor.start()

    loop = asyncio.get_event_loop()
    loop.add_reader(monitor.fileno(), on_udev_event, monitor)
    loop.run_forever()
