import pytest
from unittest.mock import AsyncMock, Mock, PropertyMock, patch, call, ANY
from inspect import isclass
import asyncio

import aserial
import gas_sensor


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
    with patch("gas_sensor.readPacket") as readPacket,\
         patch("asyncio.wait_for") as wait_for:

        gasSensor = Mock(gas_sensor.BaseSensor)
        type(gasSensor).switch_mode_cmd = PropertyMock(return_value=b"\xAA\x02\x03\x04\x05\x06\x07\x08\x09")
        type(gasSensor).approve_switch_mode = PropertyMock(return_value=b"\xBB\x02\x03\x04\x05\x06\x07\x08\x09")
        type(gasSensor).read_cmd = PropertyMock(return_value=b"\xCC\x02\x03\x04\x05\x06\x07\x08\x09")

        readPacket.side_effect = [
            b"\xFF\x86\x00\x00\x00\x00\x00\x00\x7A",
            b"\xFF\x86\x00\x00\x00\x00\x00\x00\x7A",
            gasSensor.approve_switch_mode
        ]

        async def awaitArg(arg): return await arg
        wait_for.side_effect = awaitOrRaise([awaitArg, asyncio.TimeoutError])

        port = AsyncMock(aserial.ASerial)

        with pytest.raises(gas_sensor.ASerialException):
            await gas_sensor.readSensor(port, gasSensor, lambda: None)


        port.write.assert_awaited_with(gasSensor.switch_mode_cmd)

        readPacket.assert_awaited_with(port)
        assert readPacket.call_count >= 3


@pytest.mark.asyncio
async def test_readSerial_get_sample_and_push_loop():
    with patch("gas_sensor.readPacket") as readPacket,\
         patch("asyncio.wait_for") as wait_for,\
         patch("asyncio.sleep") as sleep:

        gasSensor = Mock(gas_sensor.BaseSensor)
        type(gasSensor).switch_mode_cmd = PropertyMock(return_value=b"\xAA\x02\x03\x04\x05\x06\x07\x08\x09")
        type(gasSensor).approve_switch_mode = PropertyMock(return_value=b"\xBB\x02\x03\x04\x05\x06\x07\x08\x09")
        type(gasSensor).read_cmd = PropertyMock(return_value=b"\xCC\x02\x03\x04\x05\x06\x07\x08\x09")

        readPacket.side_effect = [
            gasSensor.approve_switch_mode,
            b"\xFF\x86\x00\x00\x00\x00\x00\x00\x7A",
            b"\xFF\x86\x00\x03\x00\x00\x00\x00\x77"
        ]

        gasSensor.parsePacket.return_value = object()

        async def awaitArg(arg): return await arg
        wait_for.side_effect = awaitOrRaise([
            awaitArg,
            awaitArg,
            awaitArg,
            asyncio.TimeoutError
        ])

        port = AsyncMock(aserial.ASerial)
        dashBoard = Mock()


        with pytest.raises(gas_sensor.ASerialException):
            await gas_sensor.readSensor(port, gasSensor, dashBoard)


        assert port.write.await_args_list == [
            ANY,
            call(gasSensor.read_cmd),
            call(gasSensor.read_cmd)
        ]

        readPacket.assert_awaited_with(port)
        assert readPacket.call_count >= 2

        dashBoard.assert_called_with(gasSensor.parsePacket.return_value)
        assert dashBoard.call_count == 2

        assert sleep.await_count == 2
