import aserial
import asyncio


async def main():
    s = aserial.ASerial("/dev/ttyUSB0", 9600)
    while True:
        c = await s.readByte()
        print(c)

asyncio.run(main())
