import asyncio
import aserial

from serial import SerialException
from asyncio import TimeoutError


class GasSensor:
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

class ZE03(GasSensor):
    _SWITCH_MODE_CMD = b"\xFF\x01\x78\x04\x00\x00\x00\x00\x83"
    _APPROVE_SWITCH_MODE = b"\xFF\x78\x01\x00\x00\x00\x00\x00\x87"
    _READ_CMD = b"\xFF\x01\x86\x04\x00\x00\x00\x00\x79"


async def readPacket(): pass


async def readSensor(port, gasSensor, dashBoard):
    try:
        async def switchMode():
            await port.write(gasSensor.switch_mode_cmd)
            while True:
                packet = await readPacket(port)
                if packet == gasSensor.approve_switch_mode:
                    return

        await asyncio.wait_for(switchMode(), 1)

        async def getSample():
            await port.write(gasSensor.read_cmd)
            return await readPacket(port)

        while True:
            sample = await asyncio.wait_for(getSample(), 1)
            item = gasSensor.parsePacket(sample)
            dashBoard(item)
            await asyncio.sleep(1)


    except (SerialException, TimeoutError) as ex:
        raise aserial.ASerialException(ex)
