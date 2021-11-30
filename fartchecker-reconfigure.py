#!/usr/bin/env python


import asyncio
import pyudev
import yaml

from reconfigure import TUI


class Dumper(yaml.Dumper):
    def increase_indent(self, flow=False, *args, **kwargs):
        return super().increase_indent(flow=flow, indentless=False)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    ui = TUI(loop)

    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by(subsystem='usb-serial')
    monitor.start()

    def on_udev_event(monitor):
        while True:
            device = monitor.poll(0)
            if device is None:
                break
            if device.action != 'bind':
                continue
            path = '/dev/{0.sys_name}'.format(device)
            location = '42'
            ui.on_found_sensor(location, path)

    loop.add_reader(monitor.fileno(), on_udev_event, monitor)

    result = ui.run()
    if result:
        print(yaml.dump(result, Dumper=Dumper))
