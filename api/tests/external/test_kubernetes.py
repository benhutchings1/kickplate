from typing import Any
from unittest.mock import AsyncMock, AsyncMock, Mock

import pytest

from entity_builders.edag import EDAGBuilder
from external.kubernetes import _NAMESPACE, KubernetesClient
from kr8s import Api
from kr8s.asyncio.objects import APIObject
from models.edag import EDAGRequest, EDAGRequestStep, EDAGResource, EDAGStepResource

pytestmark = pytest.mark.asyncio


@pytest.fixture
def edag_resource() -> EDAGResource:
    return EDAGResource(
        graphname="testgraphname",
        steps=[
            EDAGStepResource(
                stepname="step1",
                image="image1",
                replicas=1,
                dependencies=[],
                env={"type": "value1"},
                args=["step1arg"],
                command=["step1command"],
            ),
            EDAGStepResource(
                stepname="step2",
                image="image2",
                replicas=2,
                dependencies=["step2"],
                env={"type": "value2"},
                args=["step2arg"],
                command=["step2command"],
            ),
        ],
    )


async def test_should_create_edag(edag_resource: EDAGResource) -> None:
    # Arrange
    mock_api = AsyncMock(spec=Api)
    mock_resource_builder = Mock(spec=EDAGBuilder)
    mock_api_object = AsyncMock(spec=APIObject)
    client = KubernetesClient(mock_api)

    mock_resource_builder.build_manifest.return_value = mock_api_object

    # Act
    await client.create_resource(mock_resource_builder, edag_resource)

    # Assert
    assert mock_api_object.api == mock_api
    mock_resource_builder.build_manifest.assert_called_once_with(
        edag_resource, _NAMESPACE
    )
    mock_api_object.create.assert_awaited_once()
