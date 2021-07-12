import serial
import asyncio


class ASerial:
    _serial = serial.Serial(timeout=0, write_timeout=0)


    def __init__(self, port, baudrate):
        self._serial.port = port
        self._serial.baudrate = baudrate

        self._serial.open()


    async def readByte(self):
        loop = asyncio.get_running_loop()
        future = loop.create_future()

        def cb():
            d = self._serial.read(1)
            loop.remove_reader(self._serial.fileno())
            future.set_result(d)

        loop.add_reader(self._serial.fileno(), cb)

        return await future


    async def write(self, data): pass


async def readPacket(port):
    pass


async def main():
    s = ASerial("/dev/ttyUSB0", 9600)
    while True:
        c = await s.readByte()
        print(c)


if __name__ == "__main__":
    asyncio.run(main())
