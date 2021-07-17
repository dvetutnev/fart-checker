import asyncio
import aserial

from serial import SerialException
from asyncio import TimeoutError


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


async def readPacket(): pass


async def readSensor(port, gasSensor, cb):
    try:
        serial = aserial.ASerial(port, 9600)

        async def switchMode(serial):
            await serial.write(gasSensor.SWITCH_MODE_CMD)
            while True:
                packet = await readPacket(serial)
                if packet == gasSensor.APPROVE_SWITCH_MODE:
                    return

        await asyncio.wait_for(switchMode(serial), 1)

        async def getConcentration(serial):
            await serial.write(gasSensor.READ_CMD)
            return await readPacket(serial)

        while True:
            await asyncio.wait_for(getConcentration(serial), 1)


    except (SerialException, TimeoutError) as ex:
        raise aserial.ASerialException(ex)
