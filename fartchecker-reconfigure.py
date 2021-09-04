#!/usr/bin/env python


import urwid
import asyncio

import aserial
import gas_sensor


def packWidget(w):
    return urwid.Filler(urwid.AttrMap(w, None, "focus"))


class PageInflux(urwid.WidgetWrap):
    def __init__(self):
        self._widgetUrl = urwid.Edit("url", "https://")
        self._widgetOrg = urwid.Edit("org", "kysa.me")
        self._widgetBucket = urwid.Edit("bucket", "FartCHECKER")
        self._widgetToken = urwid.Edit("token")

        self._buttonNext = urwid.Button("Next")
        self._buttonCancel = urwid.Button("Cancel")

        compositeWidget = urwid.Overlay(
            urwid.LineBox(
                urwid.Pile([
                    (1, packWidget(self._widgetUrl)),
                    (1, packWidget(self._widgetOrg)),
                    (1, packWidget(self._widgetBucket)),
                    (1, packWidget(self._widgetToken)),

                    urwid.Columns([
                        packWidget(self._buttonNext),
                        packWidget(self._buttonCancel)
                    ])
                ], focus_item=0),

                title="InfluxDB"),

            urwid.SolidFill(),

            align="center", valign="middle", width=50, height=15
        )
        urwid.WidgetWrap.__init__(self, compositeWidget)

        urwid.register_signal(self.__class__, ["page_next"])
        urwid.connect_signal(self._buttonNext, "click", lambda _: urwid.emit_signal(self, "page_next"))



class PageSensors(urwid.WidgetWrap):
    def __init__(self):
        self._buttonBack = urwid.Button("Back")
        self._buttonExit = urwid.Button("Exit")
        self._buttonCancel = urwid.Button("Cancel")

        compositeWidget = urwid.Overlay(
            urwid.LineBox(
                urwid.Columns([
                    packWidget(self._buttonBack),
                    packWidget(self._buttonExit),
                    packWidget(self._buttonCancel)
                ], focus_column=1),

                title="Sensors"),

            urwid.SolidFill(),

            align="center", valign="middle", width=50, height=15
        )
        urwid.WidgetWrap.__init__(self, compositeWidget)

        urwid.register_signal(self.__class__, ["page_back"])
        urwid.connect_signal(self._buttonBack, "click", lambda _: urwid.emit_signal(self, "page_back"))



def unhandled_input(key):
    if key == "esc":
        raise urwid.ExitMainLoop()


class UI:
    def __init__(self, asyncioLoop):
        self._pageInflux = PageInflux()
        self._pageSensors = PageSensors()

        palette = [
            ("focus", "dark gray", "dark green")
        ]
        evl = urwid.AsyncioEventLoop(loop=asyncioLoop)

        self._mainLoop = urwid.MainLoop(self._pageInflux, palette, event_loop=evl, unhandled_input=unhandled_input)

        urwid.connect_signal(self._pageInflux, "page_next", self._page_next, weak_args=[self])
        urwid.connect_signal(self._pageSensors, "page_back", self._page_back, weak_args=[self])


    def _page_next(self, _):
        self._mainLoop.widget = self._pageSensors

    def _page_back(self, _):
        self._mainLoop.widget = self._pageInflux

    def run(self):
        self._mainLoop.run()


if __name__ == "__main__":
    asyncioLoop = asyncio.get_event_loop()

    ui = UI(asyncioLoop)
    ui.run()
