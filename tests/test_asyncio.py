import asyncio
from unittest.mock import Mock


def test_async_timer():
    mock = Mock()
    async def timer():
        await asyncio.sleep(0.01)
        mock()

    asyncio.run(timer())
    mock.assert_called()
