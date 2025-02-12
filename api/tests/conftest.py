from typing import Any, AsyncGenerator, Iterable

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app import app
from models.edag import (EDAG_API_VERSION, EDAG_KIND, EDAGRequest,
                         EDAGRequestStep, EDAGResource, EDAGStepResource)
from models.edagrun import EDAG_RUN_API_VERSION, EDAG_RUN_KIND, EDAGRunResource


@pytest_asyncio.fixture(scope="session")
async def async_client() -> AsyncGenerator[Any, Iterable[AsyncClient]]:
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
