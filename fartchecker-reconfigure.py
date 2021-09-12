#!/usr/bin/env python


import urwid
import asyncio
import yaml

from enum import Enum, auto

import aserial
import gas_sensor


def addAttrFocus(w):
    return urwid.AttrMap(w, None, "focus")


class ExitDialog(urwid.WidgetWrap):
    def __init__(self):
        buttonYes = urwid.Button("Yes")
        buttonNo = urwid.Button("No")

        compositeWidget = \
            urwid.Filler(
                urwid.LineBox(
                    urwid.Pile([
                        urwid.Padding(urwid.Text("Exit without save?"), align="center", width="pack"),

                        urwid.Divider(),

                        urwid.Columns([
                            urwid.Padding(addAttrFocus(buttonYes), align="center", width=8),
                            urwid.Padding(addAttrFocus(buttonNo), align="center", width=8)
                        ])
                    ])
                )
            )

        super().__init__(compositeWidget)

        urwid.register_signal(self.__class__, ["exit_yes", "exit_no"])
        urwid.connect_signal(buttonYes, "click", lambda _: self._emit("exit_yes"))
        urwid.connect_signal(buttonNo, "click", lambda _: self._emit("exit_no"))


class BasePage(urwid.PopUpLauncher):
    def __init__(self, widget):
        super().__init__(widget)

    def create_pop_up(self):
        dialog = ExitDialog()

        urwid.connect_signal(dialog, "exit_yes", lambda _: self._emit("exit_without_save"))
        urwid.connect_signal(dialog, "exit_no", lambda _: self.close_pop_up())

        return dialog

    def get_pop_up_parameters(self):
        return {'left': 10, 'top': 1, 'overlay_width': 32, 'overlay_height': 7}


class PageInflux(BasePage):
    def __init__(self):
        self._editUrl = urwid.Edit("url:    ", "https://")
        self._editOrg = urwid.Edit("org:    ", "kysa.me")
        self._editBucket = urwid.Edit("bucket: ", "FartCHECKER")
        self._editToken = urwid.Edit("token:  ")

        self._buttonNext = urwid.Button("Next")
        self._buttonCancel = urwid.Button("Cancel")

        compositeWidget = \
            urwid.LineBox(
                urwid.Pile([
                    ("pack", addAttrFocus(self._editUrl)),
                    ("pack", addAttrFocus(self._editOrg)),
                    ("pack", addAttrFocus(self._editBucket)),
                    (3, urwid.Filler(addAttrFocus(self._editToken), "top")),

                    urwid.Divider(),

                    urwid.Columns([
                       urwid.Padding(addAttrFocus(self._buttonNext), "center", width=17),
                       urwid.Padding(addAttrFocus(self._buttonCancel), "center", width=17)
                    ])
                ]),
                title="InfluxDB"
        )

        super().__init__(compositeWidget)

        urwid.register_signal(self.__class__, ["page_next", "exit_without_save"])
        urwid.connect_signal(self._buttonNext, "click", lambda _: self._emit("page_next"))
        urwid.connect_signal(self._buttonCancel, "click", lambda _: self.open_pop_up())

    @property
    def result(self):
        return {
            "url": self._editUrl.edit_text,
            "org": self._editOrg.edit_text,
            "bucket": self._editBucket.edit_text,
            "token": self._editToken.edit_text
        }


class SensorModelDialog(urwid.WidgetWrap):
    def __init__(self):
        self._buttonOk = urwid.Button("Ok")
        self._buttonSkip = urwid.Button("Skip")

        compositeWidget = \
            urwid.Filler(
                urwid.LineBox(
                    urwid.Pile([
                        ("pack", addAttrFocus(urwid.SelectableIcon("ZE03-H2S"))),

                        urwid.Divider(),

                        urwid.Columns([
                           urwid.Padding(addAttrFocus(self._buttonOk), "center", width=8),
                           urwid.Padding(addAttrFocus(self._buttonSkip), "center", width=8)
                        ])
                    ]),
                    title="Model sensor"
                )
            )

        super().__init__(compositeWidget)

        urwid.register_signal(self.__class__, ["skip"])
        urwid.connect_signal(self._buttonSkip, "click", lambda _: self._emit("skip"))


class PageSensors(BasePage):
    def __init__(self):
        self._buttonBack = urwid.Button("Back")
        self._buttonExit = urwid.Button("Save and exit")
        self._buttonCancel = urwid.Button("Cancel")

        self._sensors = urwid.SimpleFocusListWalker([addAttrFocus(urwid.SelectableIcon("--")), addAttrFocus(urwid.SelectableIcon("--"))])

        compositeWidget = \
            urwid.LineBox(
                urwid.Pile([
                    urwid.LineBox(
                        urwid.BoxAdapter(urwid.ListBox(self._sensors), 10)
                    ),
                    urwid.Columns([
                        urwid.Padding(addAttrFocus(self._buttonBack), "center", width=17),
                        urwid.Padding(addAttrFocus(self._buttonExit), "center", width=17),
                        urwid.Padding(addAttrFocus(self._buttonCancel), "center", width=17)
                    ],
                        focus_column=1
                    )
                ]),
                title="Sensors"
            )

        super().__init__(compositeWidget)

        urwid.register_signal(self.__class__, ["page_back", "exit_without_save", "save_and_exit"])
        urwid.connect_signal(self._buttonBack, "click", lambda _: self._emit("page_back"))
        urwid.connect_signal(self._buttonExit, "click", lambda _: self._emit("save_and_exit"))

        urwid.connect_signal(self._buttonCancel, "click", lambda _: self.open_dialog(self.Dialog.Exit))

    class Dialog(Enum):
        Exit = auto()
        SensorModel = auto()

    def open_dialog(self, mode: Dialog):
        if mode == self.Dialog.Exit:
            self.create_pop_up = super().create_pop_up
        elif mode == self.Dialog.SensorModel:
            self.create_pop_up = self.create_sensor_model

        self.open_pop_up()

    def create_sensor_model(self):
        dialog = SensorModelDialog()
        urwid.connect_signal(dialog, "skip", lambda _: self.close_pop_up())
        return dialog

    def add_sensor(self, model, location, path):
        self.open_dialog(self.Dialog.SensorModel)

    @property
    def result(self):
        return list()


class UI:
    def __init__(self, asyncioLoop):
        self._pageInflux = PageInflux()
        self._pageSensors = PageSensors()

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
            if key == "esc":
                raise urwid.ExitMainLoop()
            if key == "s":
                self._pageSensors.add_sensor("ZE08-CH2O", "1-3.3.2.99", "/dev/ttyUSB1{}".format(self.sensor))
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

    def run(self):
        self._mainLoop.run()
        return self._result


if __name__ == "__main__":
    asyncioLoop = asyncio.get_event_loop()

    ui = UI(asyncioLoop)
    result = ui.run()
    if result:
        print(yaml.dump(result))
