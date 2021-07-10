import asyncio
import pytest
from unittest.mock import AsyncMock, patch
from inspect import isclass

import sensor_read
from sensor_read import ZE03


class MockingSerial:
    def __init__(self, port): pass
    async def write(self, data): pass

async def mockingReadPacket(): pass

@pytest.mark.asyncio
async def test_multilpe_mock():
    async def f():
        serial = MockingSerial("/dev/ttyUSB42")
        await serial.write("dAta")
        await mockingReadPacket(serial)

    with patch(__name__ + ".MockingSerial") as serialClass,\
         patch(__name__ + ".mockingReadPacket", new_callable=AsyncMock) as readPacket:

        serialObj = serialClass.return_value
        serialObj.write = AsyncMock()

        await f()

        serialClass.assert_called_with("/dev/ttyUSB42")
        serialObj.write.assert_awaited_with("dAta")
        readPacket.assert_awaited_with(serialObj)

@pytest.mark.asyncio
async def test_several_side_effect():
    def sideEffect(items):
        def getItem():
            for item in items:
                if isclass(item) and issubclass(item, BaseException):
                    raise item
                yield item

        generator = getItem()
        def effect(*args, **kwargs):
            return next(generator)

        return effect

    mock = AsyncMock()
    mock.side_effect = sideEffect([42, 43, Exception])
    assert await mock() == 42
    assert await mock() == 43
    with pytest.raises(Exception):
        await mock()


@pytest.mark.asyncio
async def test_readSerial_open_port():
    with patch("sensor_read.ASerial") as asClass,\
         patch("asyncio.wait_for") as wait_for:

        wait_for.side_effect = asyncio.TimeoutError

        with pytest.raises(asyncio.TimeoutError):
            await sensor_read.readSensor("/dev/ttyUSB17", lambda: None)

        asClass.assert_called_with("/dev/ttyUSB17", 9600)


@pytest.mark.asyncio
async def test_readSerial_switch_mode():
    with patch("sensor_read.ASerial") as asClass,\
         patch("sensor_read.readPacket") as readPacket:

        asObject = asClass.return_value
        asObject.write = AsyncMock()

        readPacket.side_effect = [
            b"\xFF\x86\x00\x00\x00\x00\x00\x00\x7A",
            b"\xFF\x86\x00\x00\x00\x00\x00\x00\x7A",
            ZE03.APPROVE_SWITCH_MODE,
        ]

        await sensor_read.readSensor("/dev/ttyUSB17", lambda: None)

        asObject.write.assert_awaited_with(ZE03.SWITCH_MODE_CMD)

        readPacket.assert_awaited_with(asObject)
        assert readPacket.call_count == 3
