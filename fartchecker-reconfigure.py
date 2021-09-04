#!/usr/bin/env python


import urwid
import asyncio

import aserial
import gas_sensor


def unhandled_input(key):
    if key == "esc":
        raise urwid.ExitMainLoop()


class PageInflux:
    def __init__(self):
        self._widgetUrl = urwid.Edit("url", "https://")
        self._widgetOrg = urwid.Edit("org", "kysa.me")
        self._widgetBucket = urwid.Edit("bucket", "FartCHECKER")
        self._widgetToken = urwid.Edit("token")

        self._buttonNext = urwid.Button("Next")
        self._buttonCancel = urwid.Button("Cancel")

        def packWidget(w):
            return urwid.Filler(urwid.AttrMap(w, None, "focus"))

        self._compositeWidget = urwid.Overlay(
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

    @property
    def widget(self):
        return self._compositeWidget


class PageSensors:
    def __init__(self):
        self._buttonBack = urwid.Button("Back")
        self._buttonExit = urwid.Button("Exit")
        self._buttonCancel = urwid.Button("Cancel")

        def packWidget(w):
            return urwid.Filler(urwid.AttrMap(w, None, "focus"))

        self._compositeWidget = urwid.Overlay(
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

    @property
    def widget(self):
        return self._compositeWidget


class UI:
    def __init__(self, asyncioLoop):
        self._pageInflux = PageInflux()
        self._pageSensors = PageSensors()

        evl = urwid.AsyncioEventLoop(loop=asyncioLoop)

        palette = [
            ("focus", "dark gray", "dark green")
        ]

        self._mainLoop = urwid.MainLoop(self._pageSensors.widget, palette, event_loop=evl, unhandled_input=unhandled_input)


    def run(self):
        self._mainLoop.run()


if __name__ == "__main__":
    asyncioLoop = asyncio.get_event_loop()

    ui = UI(asyncioLoop)
    ui.run()
