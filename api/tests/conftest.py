import json
from typing import Any, AsyncGenerator, Generator, Iterable, cast

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app import app
from auth.security import RBACSecurity
from models.auth import Role, User
from models.edag import (
    EDAG_API_VERSION,
    EDAG_KIND,
    EDAGRequest,
    EDAGRequestStep,
    EDAGResource,
    EDAGStepResource,
)
from models.edagrun import (
    EDAG_RUN_API_VERSION,
    EDAG_RUN_KIND,
    EDAGRunResource,
    EDAGRunResponse,
)


@pytest.fixture(autouse=True)
def reset_override_dependencies() -> Generator[None, None, None]:
    original_overrides = app.dependency_overrides
    yield
    app.dependency_overrides = original_overrides


@pytest.fixture()
def mock_user(valid_token: dict[str, str]) -> User:
    return User(
        email="testuser@email.com",
        roles=[Role.KICKPLATE_USER],
        token=valid_token["token"],
    )


@pytest_asyncio.fixture()
async def async_client(mock_user: User) -> AsyncGenerator[Any, Iterable[AsyncClient]]:
    app.dependency_overrides[RBACSecurity.verify] = lambda: mock_user
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


@pytest_asyncio.fixture(scope="session")
async def auth_async_client() -> AsyncGenerator[Any, Iterable[AsyncClient]]:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


@pytest.fixture
def edag_request() -> EDAGRequest:
    return EDAGRequest(
        graphname="testgraphname",
        steps=[
            EDAGRequestStep(
                stepname="step1",
                image="image1",
                replicas=1,
                env={"type": "value1"},
                args=["step1arg"],
                command=["step1command"],
            ),
            EDAGRequestStep(
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
                dependencies=["step1"],
                env={"type": "value2"},
                args=["step2arg"],
                command=["step2command"],
            ),
        ],
    )


@pytest.fixture
def edag_manifest() -> dict[str, Any]:
    return {
        "kind": EDAG_KIND,
        "apiVersion": EDAG_API_VERSION,
        "metadata": {"name": "testgraphname", "namespace": "testnamespace"},
        "spec": {
            "steps": {
                "step1": {
                    "image": "image1",
                    "replicas": 1,
                    "argument": ["step1arg"],
                    "envs": {"type": "value1"},
                    "command": ["step1command"],
                    "dependencies": [],
                },
                "step2": {
                    "image": "image2",
                    "replicas": 2,
                    "argument": ["step2arg"],
                    "envs": {"type": "value2"},
                    "command": ["step2command"],
                    "dependencies": ["step1"],
                },
            }
        },
    }


@pytest.fixture
def edag_run_resource() -> EDAGRunResource:
    return EDAGRunResource(edagname="myedag", edag_uid="12345")


@pytest.fixture
def edag_run_manifest() -> dict[str, Any]:
    return {
        "kind": EDAG_RUN_KIND,
        "metadata": {"namespace": "testnamespace"},
        "apiVersion": EDAG_RUN_API_VERSION,
        "spec": {"edagname": "myedag"},
    }


@pytest.fixture
def edag_run_response() -> EDAGRunResponse:
    return EDAGRunResponse(id="myedag-fusngoh")


@pytest.fixture()
def data_path() -> str:
    return "tests/auth/data"


@pytest.fixture()
def valid_token(data_path: str) -> dict[str, str]:
    with open(data_path + "/token.json") as fs:
        return cast(dict[str, str], json.load(fs))


@pytest.fixture
def valid_jwks(data_path: str) -> dict[str, Any]:
    with open(data_path + "/jwks.json") as fs:
        return cast(dict[str, str], json.load(fs))


@pytest.fixture
def valid_oidc_config(data_path: str) -> dict[str, Any]:
    with open(data_path + "/oidc_config.json") as fs:
        return cast(dict[str, str], json.load(fs))
