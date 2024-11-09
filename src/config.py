"""Configuration settings for the application."""
import os
from pathlib import Path
import logging
from mem0.configs.base import MemoryConfig
from mem0.configs.embeddings import EmbedderConfig
from mem0.configs.vector_stores import VectorStoreConfig
from mem0.configs.graphs import GraphStoreConfig
from mem0.configs.llms import LlmConfig

logger = logging.getLogger("Settings")

class Settings:
    """Application settings."""

    def __init__(self):
        """Initialize settings."""
        # Initialize paths
        self.base_dir = Path(__file__).parent.parent
        self.data_dir = self.base_dir / "data"
        self.data_dir.mkdir(exist_ok=True)

        logger.info(
            "Paths initialized - base_dir: %s, data_dir: %s",
            str(self.base_dir),
            str(self.data_dir)
        )

        # API settings
        self.api_version = "0.1.0"
        self.api_prefix = "/api/v1"
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.host = os.getenv("HOST", "0.0.0.0")
        self.port = int(os.getenv("PORT", "8000"))
        self.workers = int(os.getenv("WORKERS", "1"))

        # CORS settings
        self.cors_origins = os.getenv(
            "CORS_ORIGINS",
            "http://localhost,http://localhost:3000"
        ).split(",")
        self.cors_methods = ["*"]
        self.cors_headers = ["*"]

        # Auth settings
        self.jwt_secret = os.getenv("JWT_SECRET", "your-secret-key")
        self.jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        self.refresh_token_expire_days = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

        # Memory settings
        self.memory_config = MemoryConfig(
            vector_store=VectorStoreConfig(
                provider="qdrant",
                config={
                    "url": os.getenv("QDRANT_URL", "http://localhost:6333"),
                    "collection": os.getenv("QDRANT_COLLECTION", "memories")
                }
            ),
            graph_store=GraphStoreConfig(
                provider="neo4j",
                config={
                    "url": os.getenv("NEO4J_URL", "bolt://localhost:7687"),
                    "username": os.getenv("NEO4J_USERNAME", "neo4j"),
                    "password": os.getenv("NEO4J_PASSWORD", "password")
                }
            ),
            embedder=EmbedderConfig(
                provider="openai",
                config={
                    "model": os.getenv("EMBEDDINGS_MODEL", "text-embedding-ada-002")
                }
            ),
            llm=LlmConfig(
                provider="openai",
                config={
                    "model": os.getenv("LLM_MODEL", "gpt-3.5-turbo")
                }
            ),
            custom_prompt="""
            Given the following context and query, provide a relevant response:
            Context: {context}
            Query: {query}
            Response:""".strip(),
            history_db_path=str(Path(os.getenv("HISTORY_DB_PATH", str(self.data_dir / "history.db")))),
            version="v1.0"
        )

        logger.info("Memory config updated from environment")

    def to_mem0_config(self) -> MemoryConfig:
        """Convert settings to mem0 config format."""
        return self.memory_config

settings = Settings()
