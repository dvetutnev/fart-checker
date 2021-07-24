import gas_sensor
import asyncio
from asyncio import TimeoutError

from serial import SerialException


async def readSensor(port, gasSensor, dashBoard):
    try:
        async def switchMode():
            await port.write(gasSensor.switch_mode_cmd)
            while True:
                packet = await gas_sensor.readPacket(port)
                if packet == gasSensor.approve_switch_mode:
                    return

        await asyncio.wait_for(switchMode(), 1)

        async def getSample():
            await port.write(gasSensor.read_cmd)
            return await gas_sensor.readPacket(port)

        while True:
            sample = await asyncio.wait_for(getSample(), 1)
            item = gasSensor.parsePacket(sample)
            dashBoard(item)
            await asyncio.sleep(1)


    except (SerialException, TimeoutError) as ex:
        raise gas_sensor.ASerialException(ex)
