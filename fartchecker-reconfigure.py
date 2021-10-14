#!/usr/bin/env python


import asyncio
import yaml

from reconfigure import TUI


class Dumper(yaml.Dumper):
    def increase_indent(self, flow=False, *args, **kwargs):
        return super().increase_indent(flow=flow, indentless=False)


if __name__ == "__main__":
    asyncioLoop = asyncio.get_event_loop()

    ui = TUI(asyncioLoop)
    result = ui.run()
    if result:
        print(yaml.dump(result, Dumper=Dumper))
