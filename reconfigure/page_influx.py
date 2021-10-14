import urwid
import reconfigure


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
                    ("pack", urwid.AttrMap(self._editUrl, None, "focus")),
                    ("pack", urwid.AttrMap(self._editOrg, None, "focus")),
                    ("pack", urwid.AttrMap(self._editBucket, None, "focus")),
                    (3, urwid.Filler(urwid.AttrMap(self._editToken, None, "focus"), "top")),

                    urwid.Divider(),

                    urwid.Columns([
                       urwid.Padding(urwid.AttrMap(self._buttonNext, None, "focus"), "center", width=17),
                       urwid.Padding(urwid.AttrMap(self._buttonCancel, None, "focus"), "center", width=17)
                    ])
                ]),
                title="InfluxDB"
            )

        super().__init__(compositeWidget)

        urwid.register_signal(self.__class__, ["page_next", "exit_without_save"])
        urwid.connect_signal(self._buttonNext, "click", lambda _: self._emit("page_next"))
        urwid.connect_signal(self._buttonCancel, "click", lambda _: self.open_pop_up())

    def create_pop_up(self):
        dialog = reconfigure.ExitDialog()

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
