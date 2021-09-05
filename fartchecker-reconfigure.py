#!/usr/bin/env python


import urwid
import asyncio

import aserial
import gas_sensor


def addAttrFocus(w):
    return urwid.AttrMap(w, None, "focus")

def packWidget(w):
    return urwid.Filler(addAttrFocus(w))


class ExitDialog(urwid.WidgetWrap):
    def __init__(self):
        buttonYes = urwid.Button("Yes")
        buttonNo = urwid.Button("No")

        compositeWidget = \
            urwid.Filler(
                urwid.Pile([
                    urwid.Text("Exit without save?"),
                    urwid.Columns([
                        addAttrFocus(buttonYes),
                        addAttrFocus(buttonNo)
                    ])
                ])

        )

        super().__init__(compositeWidget)

        urwid.register_signal(self.__class__, ["exit_yes", "exit_no"])
        urwid.connect_signal(buttonYes, "click", lambda _: self._emit("exit_yes"))
        urwid.connect_signal(buttonNo, "click", lambda _: self._emit("exit_no"))



class PageInflux(urwid.WidgetWrap):
    def __init__(self):
        self._editOrg = urwid.Edit("org", "kysa.me")
        self._editBucket = urwid.Edit("bucket", "FartCHECKER")
        self._editUrl = urwid.Edit("url", "https://")
        self._editToken = urwid.Edit("token")

        self._buttonNext = urwid.Button("Next")
        self._buttonCancel = urwid.Button("Cancel")

        compositeWidget = \
            urwid.Overlay(
                urwid.Filler(
                    urwid.LineBox(
                        urwid.Pile([
                            ("pack", addAttrFocus(self._editOrg)),
                            ("pack", addAttrFocus(self._editBucket)),
                            ("pack", addAttrFocus(self._editUrl)),
                            ("pack", addAttrFocus(self._editToken)),

                            urwid.Columns([
                                addAttrFocus(self._buttonNext),
                                addAttrFocus(self._buttonCancel)
                            ])
                        ]),
                        title="InfluxDB"
                    )
                ),
                urwid.SolidFill(),
                align="center", valign="middle", width=50, height=15
            )

        super().__init__(compositeWidget)

        urwid.register_signal(self.__class__, ["page_next"])
        urwid.connect_signal(self._buttonNext, "click", lambda _: self._emit("page_next"))



class PageSensors(urwid.PopUpLauncher):
    def __init__(self):
        self._buttonBack = urwid.Button("Back")
        self._buttonExit = urwid.Button("Exit")
        self._buttonCancel = urwid.Button("Cancel")

        compositeWidget = \
            urwid.Overlay(
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

        super().__init__(compositeWidget)

        urwid.register_signal(self.__class__, ["page_back"])
        urwid.connect_signal(self._buttonBack, "click", lambda _: self._emit("page_back"))

        urwid.connect_signal(self._buttonCancel, "click", lambda _: self.open_pop_up())

    def create_pop_up(self):
        dialog = ExitDialog()

        def exit_yes(_):
            raise urwid.ExitMainLoop()

        def exit_no(_):
            self.close_pop_up()

        urwid.connect_signal(dialog, "exit_yes", exit_yes)
        urwid.connect_signal(dialog, "exit_no", exit_no)

        return dialog

    def get_pop_up_parameters(self):
        return {'left': 0, 'top': 1, 'overlay_width': 32, 'overlay_height': 7}


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

        self._mainLoop = urwid.MainLoop(self._pageInflux, palette,
                                        event_loop=evl, unhandled_input=unhandled_input, pop_ups=True)

        urwid.connect_signal(self._pageInflux, "page_next", self._page_next, weak_args=[self])
        urwid.connect_signal(self._pageSensors, "page_back", self._page_back, weak_args=[self])

    def _page_next(self, _1, _2):
        self._mainLoop.widget = self._pageSensors

    def _page_back(self, _1, _2):
        self._mainLoop.widget = self._pageInflux

    def run(self):
        self._mainLoop.run()


if __name__ == "__main__":
    asyncioLoop = asyncio.get_event_loop()

    ui = UI(asyncioLoop)
    ui.run()
