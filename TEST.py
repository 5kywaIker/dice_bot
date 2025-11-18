from unittest.mock import Mock, AsyncMock
import pytest
from bot_functions import change_command

@pytest.fixture
def mock_ctx() -> Mock:
    mock = Mock()
    mock.send = AsyncMock()
    return mock

@pytest.mark.asyncio
async def test_change_command(mock_ctx):
    await change_command(mock_ctx, "damage", "1d20+13", "383707465411198976")
    mock_ctx.send.assert_awaited_once_with(100)
