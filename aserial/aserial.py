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
            byte = self._serial.read(1)
            loop.remove_reader(self._serial.fileno())
            future.set_result(byte)

        loop.add_reader(self._serial.fileno(), cb)

        return await future


    async def write(self, data):
        loop = asyncio.get_running_loop()
        event = asyncio.Event()

        def cb():
            loop.remove_writer(self._serial.fileno())
            event.set()

        loop.add_writer(self._serial.fileno(), cb)
        self._serial.write(data)

        await event.wait()
