import asyncio
import pytest
from unittest.mock import AsyncMock, patch

import sensor_read


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

    with patch(__name__ + ".MockingSerial") as serialClass, \
         patch(__name__ + ".mockingReadPacket", new_callable=AsyncMock) as readPacket:

        serialObj = serialClass.return_value
        serialObj.write = AsyncMock()

        await f()

        serialClass.assert_called_with("/dev/ttyUSB42")
        serialObj.write.assert_awaited_with("dAta")
        readPacket.assert_awaited_with(serialObj)


@pytest.mark.asyncio
async def test_readSerial_open_port():
    with patch("sensor_read.ASerial", spec=True) as asClass:
        await sensor_read.readSensor("/dev/ttyUSB17", lambda: None)
        asClass.assert_called_with("/dev/ttyUSB17", 9600)

@pytest.mark.asyncio
async def test_readSerial_switch_mode():
    with patch("sensor_read.ASerial") as asClass:
        asObject = asClass.return_value
        asObject.write = AsyncMock()

        await sensor_read.readSensor("/dev/ttyUSB17", lambda: None)

        asObject.write.assert_awaited_with(b"\xFF\x01\x78\x04\x00\x00\x00\x00\x83")
