import aserial
import asyncio


async def main():
    port = aserial.ASerial("/dev/ttyUSB0", 9600)
    data = b"Data56789"

    async def write():
        await port.write(data)

    async def read():
        result = bytes()

        while len(result) < len(data):
            result += await port.readByte()

        return result

    taskWrite = asyncio.create_task(write())
    taskRead = asyncio.create_task(read())
    await asyncio.wait([taskWrite, taskRead])

    result = taskRead.result()
    assert taskRead.result() == data

asyncio.run(main())
