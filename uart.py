# Project FartCHECKER
# UART interface for Winsen gas sensors
# Dmitriy Vetutnev, 2021


from transitions import Machine


def calc_checksum(packet):
    result = sum(packet[1:7])
    result = ~result
    result += 1
    return result & 0xFF


class Matter:
    pass


class Receiver:
    class Matter(object):
        pass

    def __init__(self):
        self._lump = self.Matter()

        states = ["wait_start", "receiving", "wait_checksum", "done"]
        transitions = [
            {"trigger": "start", "source": "wait_start", "dest": "receiving"},
            {"trigger": "checksum", "source": "receiving", "dest": "wait_checksum"},
            {"trigger": "done", "source": "wait_checksum", "dest": "done"},
            {"trigger": "restart", "source": "wait_checksum", "dest": "wait_start"}
        ]

        self._state_machine = Machine(model=self._lump, states=states, transitions=transitions, initial="wait_start")

        self._data = bytearray()

    def put(self, data):
        if self._lump.is_wait_start():
            incoming_packet = self._skip_start_byte(data)
            if not incoming_packet:
                return
            self._lump.start()
        else:
            incoming_packet = data

        last_idx = None
        if self._lump.is_receiving():
            last_idx = min(7 - len(self._data), len(incoming_packet))
            self._data += incoming_packet[:last_idx]
            if len(self._data) == 7:
                self._lump.checksum()

        if self._lump.is_wait_checksum():
            if last_idx and (last_idx < len(incoming_packet)):    # Checksum in current packet
                checksum = incoming_packet[last_idx]
            elif last_idx and (last_idx == len(incoming_packet)): # Checksum in next packet
                return
            else:                                   # Separated checksum from next packet
                checksum = incoming_packet[0]

            calculated_checksum = calc_checksum([0xFF] + list(self._data))
            if checksum == calculated_checksum:
                self._lump.done()
            else:
                self._data = bytearray()
                self._lump.restart()

    def _skip_start_byte(self, packet):
        for i, b in enumerate(packet):
            if b == 0xFF:
                return packet[i + 1:]
        return None

    def is_done(self):
        return self._lump.is_done()

    def get_data(self):
        if not self.is_done():
            raise BufferError("Not done")
        return self._data
