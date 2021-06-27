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
        return mockB()

    async def main():
        return await asyncio.gather(timerA(), timerB())

    result = asyncio.run(main())
    assert result == ["MockA", "MockB"]


def test_gather2():
    mockA = Mock(return_value="MockA")
    async def timerA():
        await asyncio.sleep(0.05)
        return mockA()

    mockB = Mock(return_value="MockB")
    async def timerB():
        await asyncio.sleep(0.02)
        return mockB()

    async def main():
        return await asyncio.gather(timerB(), timerA())

    result = asyncio.run(main())
    assert result == ["MockB", "MockA"]


def sync42():
    return 42

def syncTestingFunction():
    return sync42()

@patch(__name__ + ".sync42", new_callable=Mock)
def test_mocking_sync_function(mock):
    mock.return_value = 31
    assert syncTestingFunction() == 31


async def async42():
    await asyncio.sleep(2)
    return 42

@patch("asyncio.sleep", new_callable=AsyncMock)
def test_mocking_sleep(mock):
    result = asyncio.run(async42())
    assert result == 42
    mock.assert_awaited()


async def testingFunction():
    return await async42()

@patch(__name__ + ".async42", new_callable=AsyncMock)
def test_mocking_async_function(mock):
    mock.return_value = 117
    result = asyncio.run(testingFunction())
    assert result == 117
    mock.asert_awaited()
