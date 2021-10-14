import urwid
import reconfigure

from enum import Enum, auto


class SelectablePile(urwid.Pile):
    def __init__(self, widget_list, focus_item=None):
        urwid.register_signal(self.__class__, ["select_sensor"])
        super().__init__(widget_list, focus_item)

    def keypress(self, size, key):
        if key == "up" or key == "down":
            ret = super().keypress(size, key)
            if not ret:
                for (w, _) in self.contents:
                    w.set_attr_map({None: None})
                self.focus.set_attr_map({None: "focus"})
            return ret
        elif key == "enter":
            sensor = self.focus.original_widget.text
            self._emit("select_sensor", sensor)
        else:
            return super().keypress(size, key)


sensors = (
    "ZE03-CO",
    "ZE03-HN3",
    "ZE03-H2S",
    "ZE03-HF",
    "ZE03-O2",
    "ZE03-NO2",
    "ZE03-SO2",
    "ZE03-O3",
    "ZE03-CL2"
)


class SensorModelDialog(urwid.WidgetWrap):
    def __init__(self, location, path):
        self._buttonOk = urwid.Button("Ok")
        self._buttonSkip = urwid.Button("Skip")

        self._sensorModels = SelectablePile([
            ("pack", urwid.AttrMap(urwid.SelectableIcon(sensor), None)) for sensor in sensors
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
                           urwid.Padding(urwid.AttrMap(self._buttonOk, None, "focus"), "center", width=8),
                           urwid.Padding(urwid.AttrMap(self._buttonSkip, None, "focus"), "center", width=8)
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
                        urwid.Padding(urwid.AttrMap(self._buttonBack, None, "focus"), "center", width=17),
                        urwid.Padding(urwid.AttrMap(self._buttonExit, None, "focus"), "center", width=17),
                        urwid.Padding(urwid.AttrMap(self._buttonCancel, None, "focus"), "center", width=17)
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
        dialog = reconfigure.ExitDialog()
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
        item = urwid.AttrMap(self._Sensor(model, location, path), None, "focus")
        self._sensors.append(item)
        self.close_pop_up()

    def on_found_sensor(self, location, path):
        self.open_pop_up(self.Dialog.SensorModel, location, path)

    @property
    def result(self):
        return [item.original_widget.result for item in self._sensors]
