import urwid


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
                            urwid.Padding(urwid.AttrMap(buttonYes, None, "focus"), align="center", width=8),
                            urwid.Padding(urwid.AttrMap(buttonNo, None, "focus"), align="center", width=8)
                        ])
                    ])
                )
            )

        super().__init__(compositeWidget)

        urwid.register_signal(self.__class__, ["exit_yes", "exit_no"])
        urwid.connect_signal(buttonYes, "click", lambda _: self._emit("exit_yes"))
        urwid.connect_signal(buttonNo, "click", lambda _: self._emit("exit_no"))
