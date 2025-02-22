from unittest.mock import AsyncMock, Mock

import pytest
from httpx import Response
from kr8s import ServerError
from kr8s.asyncio.objects import APIObject

from entity_builders.edag import EDAGBuilder
from entity_builders.edagrun import EDAGRunBuilder
from external.kubernetes import KubernetesClient
from features.graph.exceptions import (
    EDAGAlreadyExistsError,
    EDAGNotFoundError,
    UndeterminedApiError,
)
from features.graph.services import EDAGServices
from models.edag import EDAGRequest, EDAGResource
from models.edagrun import EDAGRunResource

pytestmark = pytest.mark.asyncio


async def test_create_edag(edag_request: EDAGRequest, edag_resource: EDAGResource):
    # arrange
    mock_kubernetes_client = AsyncMock(spec=KubernetesClient)
    mock_edag_builder = Mock(spec=EDAGBuilder)
    mock_edag_run_builder = Mock(spec=EDAGRunBuilder)
    svc = EDAGServices(mock_kubernetes_client, mock_edag_builder, mock_edag_run_builder)

    mock_edag_builder.build_resource.return_value = edag_resource

    # act
    await svc.create_edag(edag_request)

    # assert
    mock_edag_builder.build_resource.assert_called_once_with(edag_request)
    mock_kubernetes_client.create_resource.assert_called_once_with(
        mock_edag_builder, edag_resource
    )


async def test_should_raise_error_if_edag_already_exists(
    edag_request: EDAGRequest, edag_resource: EDAGResource
) -> None:
    # arrange
    mock_kubernetes_client = AsyncMock(spec=KubernetesClient)
    mock_edag_builder = Mock(spec=EDAGBuilder)
    mock_edag_run_builder = Mock(spec=EDAGRunBuilder)
    svc = EDAGServices(mock_kubernetes_client, mock_edag_builder, mock_edag_run_builder)

    mock_edag_builder.build_resource.return_value = edag_resource

    response = Response(status_code=409)
    mock_kubernetes_client.create_resource.side_effect = ServerError(
        message="Already exists", response=response
    )

    # act
    with pytest.raises(EDAGAlreadyExistsError) as exc:
        await svc.create_edag(edag_request)

    # assert
    assert exc.value.edag_name == edag_request.graphname


async def test_should_raise_error_if_error_is_unknown_creating_edag(
    edag_request: EDAGRequest, edag_resource: EDAGResource
) -> None:
    # arrange
    mock_kubernetes_client = AsyncMock(spec=KubernetesClient)
    mock_edag_builder = Mock(spec=EDAGBuilder)
    mock_edag_run_builder = Mock(spec=EDAGRunBuilder)
    svc = EDAGServices(mock_kubernetes_client, mock_edag_builder, mock_edag_run_builder)

    mock_edag_builder.build_resource.return_value = edag_resource

    response = Response(status_code=500)
    mock_kubernetes_client.create_resource.side_effect = ServerError(
        message="Already exists", response=response
    )

    # act
    with pytest.raises(UndeterminedApiError) as exc:
        await svc.create_edag(edag_request)


async def test_run_edag(edag_run_resource: EDAGRunResource):
    # arrange
    mock_kubernetes_client = AsyncMock(spec=KubernetesClient)
    mock_edag_builder = Mock(spec=EDAGBuilder)
    mock_edag_run_builder = Mock(spec=EDAGRunBuilder)
    mock_api_object = Mock(spec=APIObject)

    svc = EDAGServices(mock_kubernetes_client, mock_edag_builder, mock_edag_run_builder)
    edag_name = edag_run_resource.edagname
    expected_edag_run_name = edag_name + "-fdsuihgiu"

    mock_api_object.raw = {"metadata": {"uid": edag_run_resource.edag_uid}}
    mock_edag_run_builder.build_resource.return_value = edag_run_resource
    mock_kubernetes_client.get_resource.return_value = mock_api_object
    mock_kubernetes_client.create_resource.return_value = {
        "metadata": {"name": expected_edag_run_name}
    }
    # act
    edag_run_response = await svc.run_edag(edag_name)

    # assert
    mock_kubernetes_client.create_resource.assert_called_once_with(
        mock_edag_run_builder, edag_run_resource
    )
    mock_kubernetes_client.get_resource.assert_called_once_with(
        mock_edag_builder, edag_name
    )
    assert edag_run_response.id == expected_edag_run_name


async def test_should_retry_if_run_name_collides(
    edag_run_resource: EDAGRunResource,
) -> None:
    # arrange
    mock_kubernetes_client = AsyncMock(spec=KubernetesClient)
    mock_edag_builder = Mock(spec=EDAGBuilder)
    mock_edag_run_builder = Mock(spec=EDAGRunBuilder)
    mock_api_object = Mock(spec=APIObject)

    svc = EDAGServices(mock_kubernetes_client, mock_edag_builder, mock_edag_run_builder)
    edag_name = edag_run_resource.edagname
    expected_edag_run_name = edag_name + "-fdsuihgiu"

    mock_api_object.raw = {"metadata": {"uid": edag_run_resource.edag_uid}}
    mock_kubernetes_client.get_resource.return_value = mock_api_object
    mock_edag_run_builder.build_resource.return_value = edag_run_resource
    mock_kubernetes_client.create_resource.side_effect = [
        ServerError(message="Already exists", response=Response(status_code=409)),
        {"metadata": {"name": expected_edag_run_name}},
    ]
    # act
    edag_run_response = await svc.run_edag(edag_name)

    # assert
    mock_kubernetes_client.create_resource.assert_called_with(
        mock_edag_run_builder, edag_run_resource
    )
    assert mock_kubernetes_client.create_resource.call_count == 2

    mock_kubernetes_client.get_resource.assert_called_with(mock_edag_builder, edag_name)
    assert mock_kubernetes_client.get_resource.call_count == 2

    assert edag_run_response.id == expected_edag_run_name


async def test_should_raise_error_if_edag_not_found(
    edag_run_resource: EDAGRunResource,
) -> None:
    # arrange
    mock_kubernetes_client = AsyncMock(spec=KubernetesClient)
    mock_edag_builder = Mock(spec=EDAGBuilder)
    mock_edag_run_builder = Mock(spec=EDAGRunBuilder)

    svc = EDAGServices(mock_kubernetes_client, mock_edag_builder, mock_edag_run_builder)
    edag_name = edag_run_resource.edagname

    mock_edag_run_builder.build_resource.return_value = edag_run_resource
    mock_kubernetes_client.get_resource.side_effect = ServerError(
        message="Not found", response=Response(status_code=404)
    )

    # act
    with pytest.raises(EDAGNotFoundError) as exc:
        await svc.run_edag(edag_name)

    # assert
    assert exc.value.edag_name == edag_name


async def test_should_raise_error_if_error_is_unknown_running_edag(
    edag_run_resource: EDAGRunResource,
) -> None:
    # arrange
    mock_kubernetes_client = AsyncMock(spec=KubernetesClient)
    mock_edag_builder = Mock(spec=EDAGBuilder)
    mock_edag_run_builder = Mock(spec=EDAGRunBuilder)

    svc = EDAGServices(mock_kubernetes_client, mock_edag_builder, mock_edag_run_builder)
    edag_name = edag_run_resource.edagname

    mock_edag_run_builder.build_resource.return_value = edag_run_resource
    mock_kubernetes_client.get_resource.side_effect = ServerError(
        message="Not found", response=Response(status_code=500)
    )

    # act
    with pytest.raises(UndeterminedApiError) as exc:
        await svc.run_edag(edag_name)


def test_get_edag_status():
    pass
