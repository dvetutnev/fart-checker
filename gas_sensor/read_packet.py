import gas_sensor


async def readPacket(port):
    packet = bytes()

    while True:
        c = await port.readByte()
        if c == b"\xFF":
            packet += c
            break

    while len(packet) < 9:
        packet += await port.readByte()

    if packet[-1] != gas_sensor.calcChecksum(packet):
        raise gas_sensor.ASerialException("Invalid checksum")

    return packet