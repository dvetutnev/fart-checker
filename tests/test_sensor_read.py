import pytest
from unittest.mock import AsyncMock, Mock, patch, call, ANY
from inspect import isclass

import asyncio
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
async def test_readSerial_switch_mode():
    with patch("sensor_read.readPacket") as readPacket,\
         patch("asyncio.wait_for") as wait_for:

        readPacket.side_effect = [
            b"\xFF\x86\x00\x00\x00\x00\x00\x00\x7A",
            b"\xFF\x86\x00\x00\x00\x00\x00\x00\x7A",
            ZE03.approve_switch_mode
        ]

        async def awaitArg(arg): return await arg
        wait_for.side_effect = awaitOrRaise([awaitArg, asyncio.TimeoutError])

        port = AsyncMock(aserial.ASerial)


        with pytest.raises(aserial.ASerialException):
            await sensor_read.readSensor(port, ZE03, lambda: None)


        port.write.assert_awaited_with(ZE03.switch_mode_cmd)

        readPacket.assert_awaited_with(port)
        assert readPacket.call_count >= 3


@pytest.mark.asyncio
async def test_readSerial_get_sample_and_push_loop():
    with patch("sensor_read.readPacket") as readPacket,\
         patch("sensor_read.ZE03.parsePacket") as parsePacket,\
         patch("asyncio.wait_for") as wait_for,\
         patch("asyncio.sleep") as sleep:

        readPacket.side_effect = [
            ZE03.approve_switch_mode,
            b"\xFF\x86\x00\x00\x00\x00\x00\x00\x7A",
            b"\xFF\x86\x00\x03\x00\x00\x00\x00\x77"
        ]

        item = object()
        parsePacket.return_value = item

        async def awaitArg(arg): return await arg
        wait_for.side_effect = awaitOrRaise([
            awaitArg,
            awaitArg,
            awaitArg,
            asyncio.TimeoutError
        ])

        port = AsyncMock(aserial.ASerial)
        dashBoard = Mock()


        with pytest.raises(aserial.ASerialException):
            await sensor_read.readSensor(port, ZE03, dashBoard)


        assert port.write.await_args_list == [
            ANY,
            call(ZE03.read_cmd),
            call(ZE03.read_cmd)
        ]

        readPacket.assert_awaited_with(port)
        assert readPacket.call_count >= 2

        dashBoard.assert_called_with(item)
        assert dashBoard.call_count == 2

        assert sleep.await_count == 2
