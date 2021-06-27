import asyncio
from unittest.mock import Mock, AsyncMock, patch


def test_timer():
    mock = Mock()
    async def timer():
        await asyncio.sleep(0.02)
        mock()

    asyncio.run(timer())
    mock.assert_called()


def test_two_timers():
    mock1 = Mock()
    async def timer1():
        await asyncio.sleep(0.01)
        mock1()

    mock2 = Mock()
    async def timer2():
        await asyncio.sleep(0.03)
        mock2()

    async def main():
        await asyncio.wait([timer1(), timer2()])

    asyncio.run(main())

    mock1.assert_called()
    mock2.assert_called()


def test_two_timers_return_values():
    mock1 = Mock(return_value="Mock1")
    async def timer1():
        await asyncio.sleep(0.03)
        return mock1()

    mock2 = Mock(return_value="Mock2")
    async def timer2():
        await asyncio.sleep(0.01)
        return mock2()

    async def main():
        done, _ = await asyncio.wait([timer1(), timer2()])
        res = list(map(lambda t: t.result(), done))
        return res

    result = asyncio.run(main())
    assert "Mock1" in result
    assert "Mock2" in result


def test_gather():
    mockA = Mock(return_value="MockA")
    async def timerA():
        await asyncio.sleep(0.05)
        return mockA()

    mockB = Mock(return_value="MockB")
    async def timerB():
        await asyncio.sleep(0.02)

    async def main1():
        return await asyncio.gather(timerA(), timerB())

    async def main2():
        return await asyncio.gather(timerB(), timerA())

    asyncio.run(main1()) == ["MockA", "MockB"]
    asyncio.run(main2()) == ["MockA", "MockB"]
