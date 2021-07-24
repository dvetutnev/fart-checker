from gas_sensor.sensor import BaseSensor


class ASerialException(Exception):
    pass


import asyncio

from serial import SerialException
from asyncio import TimeoutError


async def readPacket(): pass


async def readSensor(port, gasSensor, dashBoard):
    try:
        async def switchMode():
            await port.write(gasSensor.switch_mode_cmd)
            while True:
                packet = await readPacket(port)
                if packet == gasSensor.approve_switch_mode:
                    return

        await asyncio.wait_for(switchMode(), 1)

        async def getSample():
            await port.write(gasSensor.read_cmd)
            return await readPacket(port)

        while True:
            sample = await asyncio.wait_for(getSample(), 1)
            item = gasSensor.parsePacket(sample)
            dashBoard(item)
            await asyncio.sleep(1)


    except (SerialException, TimeoutError) as ex:
        raise ASerialException(ex)
