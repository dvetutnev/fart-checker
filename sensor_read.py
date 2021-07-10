from aserial import ASerial


class ZE03:
    SWITCH_MODE_CMD = b"\xFF\x01\x78\x04\x00\x00\x00\x00\x83"
    APPROVE_SWITCH_MODE = b"\xFF\x78\x01\x00\x00\x00\x00\x00\x87"


async def readPacket(port):
    pass


async def readSensor(port, cb):
    serial = ASerial(port, 9600)
    await serial.write(ZE03.SWITCH_MODE_CMD)
    while True:
        packet = await readPacket(serial)
        if packet == ZE03.APPROVE_SWITCH_MODE:
            break
