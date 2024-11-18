import pytest

pytestmark = pytest.mark.asyncio


async def test_skeleton() -> None:
    assert 1 == 1
