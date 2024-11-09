"""Test configuration and fixtures."""
import os
import asyncio
from typing import AsyncGenerator, Generator
import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from qdrant_client import QdrantClient
from neo4j import AsyncGraphDatabase
from dotenv import load_dotenv

from src.main import create_app
from src.config import settings
from src.services import init_services, get_memory_service

# Load test environment variables
load_dotenv("test.env")

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def app() -> FastAPI:
    """Create test application."""
    app = create_app()
    return app

@pytest.fixture(scope="session")
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Create test client."""
    async with AsyncClient(
        app=app,
        base_url="http://test"
    ) as client:
        yield client

@pytest.fixture(scope="session")
async def qdrant_client() -> AsyncGenerator[QdrantClient, None]:
    """Create Qdrant client."""
    client = QdrantClient(
        host=settings.memory_config["vector_store"]["config"]["host"],
        port=settings.memory_config["vector_store"]["config"]["port"]
    )
    yield client
    await client.close()

@pytest.fixture(scope="session")
async def neo4j_client() -> AsyncGenerator[AsyncGraphDatabase.driver, None]:
    """Create Neo4j client."""
    driver = AsyncGraphDatabase.driver(
        settings.memory_config["graph_store"]["config"]["uri"],
        auth=(
            settings.memory_config["graph_store"]["config"]["user"],
            settings.memory_config["graph_store"]["config"]["password"]
        )
    )
    yield driver
    await driver.close()

@pytest.fixture(scope="session")
async def memory_service():
    """Create memory service."""
    init_services()
    service = get_memory_service()
    yield service
    await service.cleanup()

@pytest.fixture(scope="function")
async def test_memory(memory_service):
    """Create test memory."""
    memory = await memory_service.add_memory(
        messages=[{
            "content": "Test memory content",
            "role": "user"
        }],
        metadata={
            "type": "test",
            "level": 1,
            "importance": 0.5,
            "user_id": "test-user"
        }
    )
    yield memory
    await memory_service.operations.delete_memory(memory["id"])

@pytest.fixture(scope="function")
async def test_user_token(app: FastAPI) -> str:
    """Create test user token."""
    from src.middleware.auth import auth_handler
    
    return auth_handler.create_access_token(
        user_id="test-user",
        additional_claims={"is_admin": False}
    )

@pytest.fixture(scope="function")
async def test_admin_token(app: FastAPI) -> str:
    """Create test admin token."""
    from src.middleware.auth import auth_handler
    
    return auth_handler.create_access_token(
        user_id="test-admin",
        additional_claims={"is_admin": True}
    )

@pytest.fixture(scope="function")
async def authorized_client(
    client: AsyncClient,
    test_user_token: str
) -> AsyncClient:
    """Create authorized test client."""
    client.headers["Authorization"] = f"Bearer {test_user_token}"
    return client

@pytest.fixture(scope="function")
async def admin_client(
    client: AsyncClient,
    test_admin_token: str
) -> AsyncClient:
    """Create admin test client."""
    client.headers["Authorization"] = f"Bearer {test_admin_token}"
    return client

@pytest.fixture(scope="function")
async def websocket_client(
    app: FastAPI,
    test_user_token: str
) -> AsyncGenerator:
    """Create WebSocket test client."""
    from fastapi.testclient import TestClient
    
    async with TestClient(app) as client:
        yield client.websocket_connect(
            f"/ws/memory/test-session?token={test_user_token}"
        )

@pytest.fixture(autouse=True)
async def cleanup_test_data():
    """Clean up test data after each test."""
    yield
    # Clean up vector store
    qdrant = QdrantClient(
        host=settings.memory_config["vector_store"]["config"]["host"],
        port=settings.memory_config["vector_store"]["config"]["port"]
    )
    await qdrant.delete_collection(
        settings.memory_config["vector_store"]["config"]["collection_name"]
    )
    
    # Clean up graph store
    driver = AsyncGraphDatabase.driver(
        settings.memory_config["graph_store"]["config"]["uri"],
        auth=(
            settings.memory_config["graph_store"]["config"]["user"],
            settings.memory_config["graph_store"]["config"]["password"]
        )
    )
    async with driver.session() as session:
        await session.run("MATCH (n) DETACH DELETE n")
    await driver.close()
