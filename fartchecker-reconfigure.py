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


class PageInflux(urwid.PopUpLauncher):
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

    def create_pop_up(self):
        dialog = ExitDialog()

        urwid.connect_signal(dialog, "exit_yes", lambda _: self._emit("exit_without_save"))
        urwid.connect_signal(dialog, "exit_no", lambda _: self.close_pop_up())

        return dialog

    def get_pop_up_parameters(self):
        return {'left': 10, 'top': 1, 'overlay_width': 32, 'overlay_height': 7}

    @property
    def result(self):
        return {
            "url": self._editUrl.edit_text,
            "org": self._editOrg.edit_text,
            "bucket": self._editBucket.edit_text,
            "token": self._editToken.edit_text
        }


class SelectablePile(urwid.Pile):
    def __init__(self, widget_list, focus_item=None):
        urwid.register_signal(self.__class__, ["select_sensor"])
        super().__init__(widget_list, focus_item)

    def keypress(self, size, key):
        if key == "enter":
            sensor = self.focus.original_widget.text
            self._emit("select_sensor", sensor)
        else:
            return super().keypress(size, key)


class SensorModelDialog(urwid.WidgetWrap):
    def __init__(self, location, path):
        self._buttonOk = urwid.Button("Ok")
        self._buttonSkip = urwid.Button("Skip")

        self._sensorModels = SelectablePile([
            ("pack", addAttrFocus(urwid.SelectableIcon("ZE03-CO"))),
            ("pack", addAttrFocus(urwid.SelectableIcon("ZE03-HN3"))),
            ("pack", addAttrFocus(urwid.SelectableIcon("ZE03-H2S"))),
            ("pack", addAttrFocus(urwid.SelectableIcon("ZE03-HF"))),
            ("pack", addAttrFocus(urwid.SelectableIcon("ZE03-O2"))),
            ("pack", addAttrFocus(urwid.SelectableIcon("ZE03-NO2"))),
            ("pack", addAttrFocus(urwid.SelectableIcon("ZE03-SO2"))),
            ("pack", addAttrFocus(urwid.SelectableIcon("ZE03-O3"))),
            ("pack", addAttrFocus(urwid.SelectableIcon("ZE03-CL2")))
        ])

        compositeWidget = \
            urwid.Filler(
                urwid.LineBox(
                    urwid.Pile([
                        urwid.Columns([
                            self._sensorModels,
                            urwid.Pile([
                                urwid.Text(f"location: {location}"),
                                urwid.Text(f"path: {path}")
                            ])
                        ]),
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

        urwid.register_signal(self.__class__, ["select_sensor", "skip"])
        urwid.connect_signal(self._sensorModels, "select_sensor", lambda _, model: self._emit("select_sensor", model, location, path))
        urwid.connect_signal(self._buttonSkip, "click", lambda _: self._emit("skip"))


class PopUp(urwid.PopUpLauncher):
    class Dialog(Enum):
        Exit = auto()
        SensorModel = auto()

    _pop_up_widget = None
    _pop_up_parameters = None

    def __init__(self, original_widget):
        super().__init__(original_widget)

    def create_pop_up(self, mode: Dialog, *args):
        """
        Subclass must override this method and return a tuple widget and parameters
        to be used for the pop-up.  This method is called once each time
        the pop-up is opened.
        """
        raise NotImplementedError("Subclass must override this method")

    def get_pop_up_parameters(self):
        return self._pop_up_parameters

    def open_pop_up(self, mode: Dialog, *args):
        self._pop_up_widget, self._pop_up_parameters = self.create_pop_up(mode, *args)
        self._invalidate()

    def close_pop_up(self):
        self._pop_up_widget, self._pop_up_parameters = None, None
        self._invalidate()


class PageSensors(PopUp):
    def __init__(self):
        self._buttonBack = urwid.Button("Back")
        self._buttonExit = urwid.Button("Save and exit")
        self._buttonCancel = urwid.Button("Cancel")

        self._sensors = urwid.SimpleFocusListWalker([])

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

        urwid.connect_signal(self._buttonCancel, "click", lambda _: self.open_pop_up(self.Dialog.Exit))

    def create_pop_up(self, mode, *args):
        if mode == self.Dialog.Exit:
            return self._create_exit_dialog()
        elif mode == self.Dialog.SensorModel:
            return self._create_sensor_model_dialog(*args)
        else:
            raise Exception("PageSensor: unknown mode")

    def _create_exit_dialog(self):
        dialog = ExitDialog()
        urwid.connect_signal(dialog, "exit_yes", lambda _: self._emit("exit_without_save"))
        urwid.connect_signal(dialog, "exit_no", lambda _: self.close_pop_up())
        return dialog, {'left': 10, 'top': 1, 'overlay_width': 32, 'overlay_height': 7}

    def _create_sensor_model_dialog(self, location, path):
        dialog = SensorModelDialog(location, path)
        urwid.connect_signal(dialog, "select_sensor", lambda _, *args: self._add_sensor(*args))
        urwid.connect_signal(dialog, "skip", lambda _: self.close_pop_up())
        return dialog, {'left': 5, 'top': 1, 'overlay_width': 70, 'overlay_height': 17}

    class _Sensor(urwid.SelectableIcon):
        def __init__(self, model, location, path):
            super().__init__(f"{model} {location} {path}")
            self._result = {
                "model": model,
                "location": location
            }

        @property
        def result(self):
            return self._result

    def _add_sensor(self, model, location, path):
        item = addAttrFocus(self._Sensor(model, location, path))
        self._sensors.append(item)
        self.close_pop_up()

    def on_found_sensor(self, location, path):
        self.open_pop_up(self.Dialog.SensorModel, location, path)

    @property
    def result(self):
        return [item.original_widget.result for item in self._sensors]


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

    def run(self):
        self._mainLoop.run()
        return self._result


class Dumper(yaml.Dumper):
    def increase_indent(self, flow=False, *args, **kwargs):
        return super().increase_indent(flow=flow, indentless=False)


if __name__ == "__main__":
    asyncioLoop = asyncio.get_event_loop()

    ui = UI(asyncioLoop)
    result = ui.run()
    if result:
        print(yaml.dump(result, Dumper=Dumper))
