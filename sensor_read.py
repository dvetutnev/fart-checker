from aserial import ASerial


async def readSensor(port, cb):
    serial = ASerial(port, 9600)
    await serial.write(b"\xFF\x01\x78\x04\x00\x00\x00\x00\x83")

