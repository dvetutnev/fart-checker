from aserial import ASerial


async def readPacket(port):
    pass


async def readSensor(port, cb):
    serial = ASerial(port, 9600)
    await serial.write(b"\xFF\x01\x78\x04\x00\x00\x00\x00\x83")
    while True:
        packet = await readPacket(serial)
        if packet == b"\xFF\x78\x01\x00\x00\x00\x00\x00\x87":
            break
