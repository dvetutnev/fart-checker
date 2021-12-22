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

    lastByte = packet[-1]
    checksum = gas_sensor.calcChecksum(packet)
    if lastByte != checksum:
        raise gas_sensor.ASerialException("Invalid checksum")

    return packet