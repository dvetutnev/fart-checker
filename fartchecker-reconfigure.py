import urwid
import asyncio

import aserial
import gas_sensor


def unhandled_input(key):
    if key == "esc":
        raise urwid.ExitMainLoop()


if __name__ == "__main__":
    asyncioLoop = asyncio.get_event_loop()

    txt = urwid.Text("FartCHECKER")
    widget = urwid.Filler(txt)
    evl = urwid.AsyncioEventLoop(loop=asyncioLoop)
    mainLoop = urwid.MainLoop(widget, event_loop=evl, unhandled_input=unhandled_input)

    port = aserial.ASerial("/dev/ttyUSB0", 9600)
    sensor = gas_sensor.ZE03(gas_sensor.Gas.CO)
    def dashBoard(measure):
        txt.set_text(str(measure))

    asyncioLoop.create_task(gas_sensor.readSensor(port, sensor, dashBoard))

    mainLoop.run()
