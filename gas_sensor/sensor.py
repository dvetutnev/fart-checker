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

    def parsePacket(self, packet):
        return None


class Measure:
    def __init__(self, name, value):
        self._name = name
        self._value = value

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return self._value

    def __str__(self):
        return "{0} {1}".format(self.name, self.value)


class ZE03(BaseSensor):
    _SWITCH_MODE_CMD = b"\xFF\x01\x78\x04\x00\x00\x00\x00\x83"
    _APPROVE_SWITCH_MODE = b"\xFF\x78\x01\x00\x00\x00\x00\x00\x87"
    _READ_CMD = b"\xFF\x01\x86\x00\x00\x00\x00\x00\x79"

    _FACTOR = {
        "CO": 1,
        "NH3": 1,
        "H2S": 1,
        "HF": 1,
        "O2": 0.1,
        "NO2": 0.1,
        "SO2": 0.1,
        "O3": 0.1,
        "CL2": 0.1
    }


    def __init__(self, name):
        if name not in self._FACTOR:
            raise Exception("Unknown sensor type")

        self._name = name
        self._factor = self._FACTOR[name]


    def parsePacket(self, packet):
        value = int(packet[2]) * 256 + int(packet[3])
        value *= self._factor
        return Measure(self._name, value)
