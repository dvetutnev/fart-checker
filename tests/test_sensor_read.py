import pytest
from unittest.mock import AsyncMock, patch
from inspect import isclass

from serial import SerialException

import aserial
import sensor_read
from sensor_read import ZE03


def awaitOrRaise(items):
    def getItem():
        for item in items:
            if isclass(item) and issubclass(item, BaseException):
                raise item
            yield item

    generator = getItem()

    async def effect(arg, *args, **kwargs):
        f = next(generator)
        return await f(arg)

    return effect

@pytest.mark.asyncio
async def test_awaitOrRaise():
    async def awaitArg(arg):
        return await arg

    mock = AsyncMock()
    mock.side_effect = awaitOrRaise([awaitArg, Exception])

    aFunction = AsyncMock(return_value=489)
    coroFunction = aFunction()
    assert await mock(coroFunction) == 489

    with pytest.raises(Exception):
        await mock(coroFunction)

    aFunction.assert_awaited_once()


@pytest.mark.asyncio
async def test_readSerial_open_port():
    with patch("aserial.ASerial") as asClass:

        asClass.side_effect = SerialException

        with pytest.raises(aserial.ASerialException):
            await sensor_read.readSensor("/dev/ttyUSB17", ZE03, lambda: None)

        asClass.assert_called_with("/dev/ttyUSB17", 9600)


@pytest.mark.asyncio
async def test_readSerial_switch_mode():
    with patch("aserial.ASerial", spec=aserial.ASerial) as asClass,\
         patch("sensor_read.readPacket") as readPacket:

        asObject = asClass.return_value

        readPacket.side_effect = [
            b"\xFF\x86\x00\x00\x00\x00\x00\x00\x7A",
            b"\xFF\x86\x00\x00\x00\x00\x00\x00\x7A",
            ZE03.APPROVE_SWITCH_MODE
        ]

        await sensor_read.readSensor("/dev/ttyUSB17", ZE03, lambda: None)

        asObject.write.assert_awaited_with(ZE03.SWITCH_MODE_CMD)

        readPacket.assert_awaited_with(asObject)
        assert readPacket.call_count >= 3
