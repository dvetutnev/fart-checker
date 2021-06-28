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


@pytest.mark.asyncio
async def test_timer():
    mock = Mock()
    async def timer():
        await asyncio.sleep(0.02)
        mock()

    await timer()
    mock.assert_called()


@pytest.mark.asyncio
async def test_two_timers():
    mock1 = Mock()
    async def timer1():
        await asyncio.sleep(0.01)
        mock1()

    mock2 = Mock()
    async def timer2():
        await asyncio.sleep(0.03)
        mock2()

    await asyncio.wait([timer1(), timer2()])

    mock1.assert_called()
    mock2.assert_called()


@pytest.mark.asyncio
async def test_two_timers_return_values():
    async def timer1():
        await asyncio.sleep(0.03)
        return 119

    async def timer2():
        await asyncio.sleep(0.01)
        return 911

    done, _ = await asyncio.wait([timer1(), timer2()])
    result = list(map(lambda t: t.result(), done))

    assert 119 in result
    assert 911 in result


@pytest.mark.asyncio
async def test_gather():
    async def timerA():
        await asyncio.sleep(0.05)
        return "aaa"

    async def timerB():
        await asyncio.sleep(0.02)
        return "bbb"

    result = await asyncio.gather(timerA(), timerB())

    assert result == ["aaa", "bbb"]


@pytest.mark.asyncio
async def test_gather2():
    async def timerA():
        await asyncio.sleep(0.05)
        return "aaa"

    async def timerB():
        await asyncio.sleep(0.02)
        return "bbb"

    result = await asyncio.gather(timerB(), timerA())

    assert result == ["bbb", "aaa"]


def sync42():
    return 42

def syncTestingFunction():
    return sync42()

@patch(__name__ + ".sync42", new_callable=Mock)
def test_mocking_sync_function(mock):
    mock.return_value = 31
    assert syncTestingFunction() == 31


async def async42():
    await asyncio.sleep(22)
    return 42

@pytest.mark.asyncio
@patch("asyncio.sleep", new_callable=AsyncMock)
async def test_mocking_sleep(mock):
    result = await async42()
    assert result == 42
    mock.assert_awaited()


async def testingFunction():
    return await async42()

@pytest.mark.asyncio
@patch(__name__ + ".async42", new_callable=AsyncMock)
async def test_mocking_async_function(mock):
    mock.return_value = 117
    result = await testingFunction()
    assert result == 117
    mock.asert_awaited()


@pytest.mark.asyncio
async def test_asyncio_wait_first():
    async def f1():
        await asyncio.sleep(0.04)
        return "f1"

    async def f2():
        await asyncio.sleep(0.02)
        return "f2"

    done, _ = await asyncio.wait([f2(), f1()], return_when=asyncio.FIRST_COMPLETED)
    for r in done:
        assert r.result() == "f2"


@pytest.mark.asyncio
async def test_asyncio_wait_for_normal():
    async def f():
        await asyncio.sleep(0.01)
        return 73

    result = await asyncio.wait_for(f(), timeout=0.05)

    assert result == 73


@pytest.mark.asyncio
async def test_asyncio_wait_for_timeout():
    async def f():
        await asyncio.sleep(0.05)
        return 73

    try:
        await asyncio.wait_for(f(), timeout=0.01)
        assert False
    except asyncio.TimeoutError:
        pass


# async def asyncFoo(): pass
#
# async def fPending():
#     result = await asyncFoo()
#     return result
#
# async def fDone():
#     result = await asyncFoo()
#     return result
#
# @pytest.mark.asyncio
# @patch(__name__ + ".asyncFoo", new_callable=AsyncMock)
# @patch(__name__ + ".asyncFoo", new_callable=AsyncMock)
# async def test_mock_awittable(mockDone, mockPending):
#     mockPending.return_value = asyncio.Future()
#     mockDone.return_value = 951
#
#     done, _ = await asyncio.wait([fPending(), fDone()], return_when=asyncio.FIRST_COMPLETED)
#     for r in done:
#         assert r.result() == 951
