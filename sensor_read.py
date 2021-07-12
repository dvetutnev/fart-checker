import asyncio

from aserial import ASerial, readPacket


class GasSensor:
    SWITCH_MODE_CMD = None
    APPROVE_SWITCH_MODE = None
    READ_CMD = None

    @staticmethod
    def parsePacket(packet):
        return None

class ZE03(GasSensor):
    SWITCH_MODE_CMD = b"\xFF\x01\x78\x04\x00\x00\x00\x00\x83"
    APPROVE_SWITCH_MODE = b"\xFF\x78\x01\x00\x00\x00\x00\x00\x87"
    READ_CMD = b"\xFF\x01\x86\x04\x00\x00\x00\x00\x79"


async def switchMode(serial, gasSensor):
    await serial.write(gasSensor.SWITCH_MODE_CMD)
    while True:
        packet = await readPacket(serial)
        if packet == gasSensor.APPROVE_SWITCH_MODE:
            return


async def readSensor(port, gasSensor, cb):
    serial = ASerial(port, 9600)
    await asyncio.wait_for(switchMode(serial, gasSensor), 1)
