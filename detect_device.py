#!/usr/bin/env python


import pyudev
import asyncio


def on_udev_event(monitor):
    while True:
        device = monitor.poll(0)
        if device is None:
            break
        print('{0.action} on {0.device_path}'.format(device))

if __name__ == "__main__":
    print(pyudev.udev_version())

    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by(subsystem='usb-serial')
    monitor.start()

    loop = asyncio.get_event_loop()
    loop.add_reader(monitor.fileno(), on_udev_event, monitor)
    loop.run_forever()
