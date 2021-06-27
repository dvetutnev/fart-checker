import asyncio
from unittest.mock import Mock


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
        result = list(map(lambda t: t.result(), done))
        return result

    res = asyncio.run(main())
    assert res == ["Mock1", "Mock2"]


    async def main2():
        done, _ = await asyncio.wait([timer2(), timer1()]) # Coro order
        result = list(map(lambda t: t.result(), done))
        return result

    res = asyncio.run(main2())
    assert res == ["Mock2", "Mock1"]
