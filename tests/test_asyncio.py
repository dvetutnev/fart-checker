import asyncio
import pytest
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


def test_asyncio_wait_first():
    async def f1():
        await asyncio.sleep(0.04)
        return "f1"

    async def f2():
        await asyncio.sleep(0.02)
        return "f2"

    async def main():
        done, _ = await asyncio.wait([f2(), f1()], return_when=asyncio.FIRST_COMPLETED)
        for r in done:
            return r.result()

    result = asyncio.run(main())
    assert result == "f2"


def test_asyncio_wait_normal():
    async def f():
        await asyncio.sleep(0.01)
        return 43

    async def main():
        done, _ = await asyncio.wait([f()], timeout=0.05)
        for r in done:
            return r.result()

    result = asyncio.run(main())
    assert result == 43


def test_asyncio_wait_for_normal():
    async def f():
        await asyncio.sleep(0.01)
        return 73

    async def main():
        return await asyncio.wait_for(f(), timeout=0.05)

    result = asyncio.run(main())
    assert result == 73


def test_asyncio_wait_for_timeout():
    async def f():
        await asyncio.sleep(0.05)
        return 73

    async def main():
        try:
            return await asyncio.wait_for(f(), timeout=0.01)
        except asyncio.TimeoutError:
            return None


    result = asyncio.run(main())
    assert result is None


async def asyncFoo(): pass

async def fPending():
    result = await asyncFoo()
    return result

async def fDone():
    result = await asyncFoo()
    return result

@pytest.mark.asyncio
@patch(__name__ + ".asyncFoo", new_callable=AsyncMock)
@patch(__name__ + ".asyncFoo", new_callable=AsyncMock)
async def test_mock_awittable(mockDone, mockPending):
    mockPending.return_value = asyncio.Future()
    mockDone.return_value = 951

    done, _ = await asyncio.wait([fPending(), fDone()], return_when=asyncio.FIRST_COMPLETED)
    for r in done:
        assert r.result() == 951
