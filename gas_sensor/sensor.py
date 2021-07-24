class BaseSensor:
    _SWITCH_MODE_CMD = None
    _APPROVE_SWITCH_MODE = None
    _READ_CMD = None

    @property
    def switch_mode_cmd(self):
        return self._SWITCH_MODE_CMD

    @property
    def approve_switch_mode(self):
        return self._APPROVE_SWITCH_MODE

    @property
    def read_cmd(self):
        return self._READ_CMD

    def parsePacket(packet):
        return None


class ZE03(BaseSensor):
    _SWITCH_MODE_CMD = b"\xFF\x01\x78\x04\x00\x00\x00\x00\x83"
    _APPROVE_SWITCH_MODE = b"\xFF\x78\x01\x00\x00\x00\x00\x00\x87"
    _READ_CMD = b"\xFF\x01\x86\x04\x00\x00\x00\x00\x79"
