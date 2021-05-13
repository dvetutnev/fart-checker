# Project FartCHECKER
# UART interface for Winsen gas sensors
# Dmitriy Vetutnev, 2021


from transitions import Machine
from typing import Final


def calc_checksum(packet):
    result = sum(packet[1:7])
    result = ~result
    result += 1
    return result & 0xFF


class Receiver:
    START_BYTE: Final = 0xFF
    DATA_LENGTH: Final = 7

    class Matter(object):
        pass

    def __init__(self, callback):
        self._callback = callback

        self._lump = Receiver.Matter()
        states = ["wait_start", "receiving", "wait_checksum"]
        transitions = [
            {"trigger": "start", "source": "wait_start", "dest": "receiving"},
            {"trigger": "checksum", "source": "receiving", "dest": "wait_checksum"},
            {"trigger": "restart", "source": "wait_checksum", "dest": "wait_start"}
        ]
        self._state_machine = Machine(model=self._lump, states=states, transitions=transitions, initial="wait_start")

        self._buffer = bytearray()

    def input(self, b):
        if self._lump.is_wait_start():
            if b == self.START_BYTE:
                self._lump.start()
            return

        if self._lump.is_receiving():
            self._buffer += bytes([b])
            if len(self._buffer) == self.DATA_LENGTH:
                self._lump.checksum()
            return

        if self._lump.is_wait_checksum():
            checksum = calc_checksum([self.START_BYTE] + list(self._buffer))
            if checksum == b:
                self._callback(self._buffer)

            self._lump.restart()
            self._buffer = bytearray()
            return
