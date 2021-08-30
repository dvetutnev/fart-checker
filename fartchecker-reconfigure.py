import urwid
import asyncio

import aserial
import gas_sensor


def unhandled_input(key):
    if key == "esc":
        raise urwid.ExitMainLoop()


if __name__ == "__main__":

    txt = urwid.Text("FartCHECKER")
    ftxt = urwid.Filler(txt)

    url = urwid.Edit("url", "https://")
    furl = urwid.Filler(urwid.AttrMap(url, None, "focus"))

    org = urwid.Edit("org", "")
    forg = urwid.Filler(urwid.AttrMap(org, None, "focus"))

    pile = urwid.Pile([ftxt, furl, forg], furl)

    palette = [
        ("focus", "dark gray", "dark green")
    ]

    asyncioLoop = asyncio.get_event_loop()
    evl = urwid.AsyncioEventLoop(loop=asyncioLoop)

    mainLoop = urwid.MainLoop(pile, palette, event_loop=evl, unhandled_input=unhandled_input)

    #port = aserial.ASerial("/dev/ttyUSB0", 9600)
    #sensor = gas_sensor.ZE03(gas_sensor.Gas.CO)
    # def dashBoard(measure):
    #     txt.set_text(str(measure))
    #
    # asyncioLoop.create_task(gas_sensor.readSensor(port, sensor, dashBoard))

    mainLoop.run()
