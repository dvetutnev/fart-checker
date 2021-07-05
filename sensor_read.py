from aserial import ASerial


async def readSensor(port, cb):
    serial = ASerial(port)

