#!/usr/bin/env python


import pyudev

if __name__ == "__main__":
    print(pyudev.udev_version())

    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by(subsystem='usb-serial')
    for action, device in monitor:
        print('{0}: {1}'.format(action, device))
