import urwid
import reconfigure


class TUI:
    def __init__(self, asyncioLoop):
        self._pageInflux = reconfigure.PageInflux()
        self._pageSensors = reconfigure.PageSensors()

        self._result = None

        def packWidget(w):
            return urwid.Overlay(
                   urwid.Filler(w),
                   urwid.SolidFill(),
                   align="center", valign="middle", width=70, height=20
            )

        self._widgets = {
            "influx": packWidget(self._pageInflux),
            "sensors": packWidget(self._pageSensors)
        }

        palette = [
            ("focus", "dark gray", "dark green")
        ]
        evl = urwid.AsyncioEventLoop(loop=asyncioLoop)

        self.sensor = 0

        def unhandled_input(key):
            if key == "f12":
                raise urwid.ExitMainLoop()
            if key == "s":
                self._pageSensors.on_found_sensor("1-3.3.2.99", "/dev/ttyUSB1{}".format(self.sensor))
                self.sensor += 1

        self._mainLoop = urwid.MainLoop(self._widgets["influx"], palette,
                                        event_loop=evl, unhandled_input=unhandled_input, pop_ups=True)

        def modeSensors(_):
            self._mainLoop.widget = self._widgets["sensors"]
        urwid.connect_signal(self._pageInflux, "page_next", modeSensors)

        def modeInflux(_):
            self._mainLoop.widget = self._widgets["influx"]
        urwid.connect_signal(self._pageSensors, "page_back", modeInflux)

        def save_and_exit(_):
            self._result = {
                "influxdb": self._pageInflux.result,
                "sensors": self._pageSensors.result
            }
            raise urwid.ExitMainLoop()
        urwid.connect_signal(self._pageSensors, "save_and_exit", save_and_exit)

        def exit_without_save(_):
            raise urwid.ExitMainLoop()
        urwid.connect_signal(self._pageInflux, "exit_without_save", exit_without_save)
        urwid.connect_signal(self._pageSensors, "exit_without_save", exit_without_save)

    def on_found_sensor(self, location, path):
        self._pageSensors.on_found_sensor("1-3.3.2.99", path)

    def run(self):
        self._mainLoop.run()
        return self._result
