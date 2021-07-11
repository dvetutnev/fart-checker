import asyncio
import pytest
from unittest.mock import AsyncMock, Mock, patch
from inspect import isclass

import aserial
import sensor_read
from sensor_read import ZE03


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

@pytest.mark.asyncio
async def test_several_side_effect():
    mock = AsyncMock()
    mock.side_effect = sideEffect([42, 43, Exception])
    assert await mock() == 42
    assert await mock() == 43
    with pytest.raises(Exception):
        await mock()


def sideEffect2(items):
    def getItem():
        for item in items:
            if isclass(item) and issubclass(item, BaseException):
                raise item
            yield item

    generator = getItem()

    async def effect(arg):
        f = next(generator)
        result = await f(arg)
        return result

    return effect

@pytest.mark.asyncio
async def test_several_side_effect2():
    async def awaitArg(arg):
        await arg
        return 42

    mock = AsyncMock()
    coro = mock()

    sf = sideEffect2([awaitArg, Exception])

    await sf(coro)
    with pytest.raises(Exception):
        await sf(coro)

    mock.assert_awaited_once()


@pytest.mark.asyncio
async def test_readSerial_open_port():
    with patch("sensor_read.ASerial") as asClass,\
         patch("asyncio.wait_for") as wait_for:

        wait_for.side_effect = asyncio.TimeoutError

        with pytest.raises(asyncio.TimeoutError):
            await sensor_read.readSensor("/dev/ttyUSB17", ZE03, lambda: None)

        asClass.assert_called_with("/dev/ttyUSB17", 9600)


@pytest.mark.asyncio
async def test_switchMode():
    with patch("sensor_read.readPacket") as readPacket:
        serial = AsyncMock(spec=aserial.ASerial)

        readPacket.side_effect = [
            b"\xFF\x86\x00\x00\x00\x00\x00\x00\x7A",
            b"\xFF\x86\x00\x00\x00\x00\x00\x00\x7A",
            ZE03.APPROVE_SWITCH_MODE
        ]

        await sensor_read.switchMode(serial, ZE03)

        serial.write.assert_awaited_with(ZE03.SWITCH_MODE_CMD)

        readPacket.assert_awaited_with(serial)
        assert readPacket.call_count == 3
