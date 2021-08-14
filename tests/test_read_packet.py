# Project FartCHECKER
# Test for read packet
# Dmitriy Vetutnev, 2021


import pytest
from unittest.mock import AsyncMock

import aserial
import gas_sensor


@pytest.mark.asyncio
async def test_normal():
    port = AsyncMock(aserial.ASerial)
    port.readByte.side_effect = [
        b"\xFF", b"\x86", b"\x00", b"\x03", b"\x00", b"\x00", b"\x00", b"\x00", b"\x77"
    ]

    assert await gas_sensor.readPacket(port) == b"\xFF\x86\x00\x03\x00\x00\x00\x00\x77"


@pytest.mark.asyncio
async def test_invalid_checksum():
    port = AsyncMock(aserial.ASerial)
    port.readByte.side_effect = [
        b"\xFF", b"\x86", b"\x00", b"\x03", b"\x00", b"\x00", b"\x00", b"\x00", b"\xAA"
    ]

    with pytest.raises(gas_sensor.ASerialException):
        await gas_sensor.readPacket(port)


@pytest.mark.asyncio
async def test_wait_start():
    port = AsyncMock(aserial.ASerial)
    port.readByte.side_effect = [
        b"\x01", b"\x02",
        b"\xFF", b"\x86", b"\x00", b"\x00", b"\x00", b"\x00", b"\x00", b"\x00", b"\x7A"
    ]

    assert await gas_sensor.readPacket(port) == b"\xFF\x86\x00\x00\x00\x00\x00\x00\x7A"
