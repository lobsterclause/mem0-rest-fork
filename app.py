# pylint: disable=undefined-variable
import os
import json
import uuid
import hashlib
import logging
import sys
from datetime import datetime

import pytz
from dotenv import load_dotenv
from flask import Blueprint, Flask, Response, request, jsonify
from mem0 import Memory
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import PointStruct

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Set OpenAI API key from environment
openai_api_key = os.getenv('OPENAI_API_KEY')
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set")
os.environ["OPENAI_API_KEY"] = openai_api_key

app = Flask(__name__)
app.url_map.strict_slashes = False
app.debug = True

api = Blueprint("api", __name__, url_prefix="/v1")

# Initialize Qdrant client - connect to Docker service
qdrant_client = QdrantClient(host="localhost", port=6333)

# Check if collection exists, create only if it doesn't
try:
    collections = qdrant_client.get_collections()
    if "memories" not in [c.name for c in collections.collections]:
        logger.info("Creating new memories collection")
        qdrant_client.create_collection(
            collection_name="memories",
            vectors_config=models.VectorParams(
                size=3072,  # text-embedding-3-large dimension size
                distance=models.Distance.COSINE
            )
        )
    else:
        logger.info("Using existing memories collection")
except Exception as e:
    logger.error(f"Error checking/creating collection: {str(e)}")
    raise

# Configure memory with required settings
config = {
    "version": "v1.1",
    "llm": {
        "provider": "openai_structured",
        "config": {
            "model": os.getenv("OPENAI_MODEL", "gpt-4-1106-preview"),
            "api_key": openai_api_key
        }
    },
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": "localhost",  # Connect to Docker service
            "port": 6333,
            "collection_name": "memories",
            "embedding_model_dims": 3072  # text-embedding-3-large dimension size
        }
    },
    "embedder": {
        "provider": "openai",
        "config": {
            "model": "text-embedding-3-large",
            "api_key": openai_api_key
        }
    }
}

# Initialize memory with config
memory = Memory.from_config(config)

def generate_memory_id(content, timestamp, user_id, agent_id=None):
    """Generate a deterministic memory ID"""
    id_string = f"{content}{timestamp}{user_id}{agent_id or ''}"
    return hashlib.sha256(id_string.encode()).hexdigest()[:32]

@api.route("/memories/<memory_id>", methods=["GET"])
def get_memory(memory_id):
    """Get a memory by ID."""
    try:
        logger.info(f"Retrieving memory with ID: {memory_id}")
        
        # Convert memory_id to integer hash for Qdrant lookup
        point_id = hash(memory_id) & ((1 << 63) - 1)
        
        # Get point from Qdrant
        points = qdrant_client.retrieve(
            collection_name="memories",
            ids=[point_id]
        )
        
        if not points:
            logger.error(f"Memory not found: {memory_id}")
            return jsonify({"message": "Memory not found"}), 404
            
        point = points[0]
        payload = point.payload
        
        # Format response
        response_data = {
            "id": payload.get("id"),
            "content": payload.get("content"),
            "messages": payload.get("messages", []),  # Include original messages
            "metadata": {
                "user_id": payload.get("user_id"),
                "agent_id": payload.get("agent_id")
            }
        }
        
        # Add any additional metadata
        for key, value in payload.items():
            if key not in ["id", "content", "messages", "user_id", "agent_id"]:
                response_data["metadata"][key] = value
        
        logger.info(f"Retrieved memory: {response_data}")
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error retrieving memory: {str(e)}", exc_info=True)
        return jsonify({"message": str(e)}), 400

@api.route("/memories/<memory_id>", methods=["PUT"])
def update_memory(memory_id):
    """Update an existing memory."""
    try:
        logger.info(f"Updating memory with ID: {memory_id}")
        body = request.get_json()
        logger.info(f"Request body: {body}")
        
        messages = body.get("messages", [])
        user_id = body.get("user_id")
        agent_id = body.get("agent_id")
        metadata = body.get("metadata", {})
        
        # Convert memory_id to integer hash for Qdrant lookup
        point_id = hash(memory_id) & ((1 << 63) - 1)
        
        # Check if memory exists
        points = qdrant_client.retrieve(
            collection_name="memories",
            ids=[point_id]
        )
        
        if not points:
            logger.error(f"Memory not found: {memory_id}")
            return jsonify({"message": "Memory not found"}), 404
        
        # Generate new content
        content = "\n".join(f"{msg['role']}: {msg['content']}" for msg in messages)
        
        # Get embedding for new content
        embedding = memory.embedding_model.embed(content)
        
        # Update point in Qdrant
        point = PointStruct(
            id=point_id,
            vector=embedding,
            payload={
                "id": memory_id,
                "content": content,
                "messages": messages,
                "user_id": user_id,
                "agent_id": agent_id,
                **metadata
            }
        )
        qdrant_client.upsert(
            collection_name="memories",
            points=[point]
        )
        
        # Update memory using mem0's add method
        result = memory.add(
            messages=messages,
            user_id=user_id,
            agent_id=agent_id,
            metadata={"id": memory_id, "content": content, **metadata}
        )
        
        logger.info(f"Memory update result: {result}")
        
        response_data = {
            "id": memory_id,
            "content": content,
            "messages": messages,
            "metadata": {
                "user_id": user_id,
                "agent_id": agent_id,
                **metadata
            },
            "results": result.get('results', []),
            "relations": result.get('relations', [])
        }
        
        logger.info(f"Sending response: {response_data}")
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error updating memory: {str(e)}", exc_info=True)
        return jsonify({"message": str(e)}), 400

@api.route("/memories", methods=["POST"])
def add_memories():
    try:
        logger.info("Received add_memories request")
        body = request.get_json()
        logger.info(f"Request body: {body}")
        
        messages = body.get("messages", [])
        user_id = body.get("user_id")
        agent_id = body.get("agent_id")
        metadata = body.get("metadata", {})
        
        logger.info(f"Adding memory with messages={messages}, user_id={user_id}, agent_id={agent_id}")
        
        # Generate memory ID
        content = "\n".join(f"{msg['role']}: {msg['content']}" for msg in messages)
        timestamp = datetime.now(pytz.UTC).isoformat()
        memory_id = generate_memory_id(content, timestamp, user_id, agent_id)
        
        # Get embedding for content
        embedding = memory.embedding_model.embed(content)
        
        # Store point in Qdrant
        point = PointStruct(
            id=hash(memory_id) & ((1 << 63) - 1),  # Convert string ID to positive integer
            vector=embedding,
            payload={
                "id": memory_id,
                "content": content,
                "messages": messages,  # Store original messages for reconstruction
                "user_id": user_id,
                "agent_id": agent_id,
                **metadata
            }
        )
        qdrant_client.upsert(
            collection_name="memories",
            points=[point]
        )
        
        # Add memory using mem0's add method
        result = memory.add(
            messages=messages,
            user_id=user_id,
            agent_id=agent_id,
            metadata={"id": memory_id, "content": content, **metadata}
        )
        
        logger.info(f"Memory add result: {result}")
        
        response_data = {
            "id": memory_id,
            "content": content,
            "messages": messages,
            "metadata": {
                "user_id": user_id,
                "agent_id": agent_id,
                **metadata
            },
            "results": result.get('results', []),
            "relations": result.get('relations', [])
        }
        
        logger.info(f"Sending response: {response_data}")
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error in add_memories: {str(e)}", exc_info=True)
        return jsonify({"message": str(e)}), 400

@api.route("/memories/search", methods=["POST"])
def search_memories():
    try:
        logger.info("Received search_memories request")
        body = request.get_json()
        logger.info(f"Request body: {body}")
        
        query = body.get("query", "")
        filters = body.get("filters", {})
        limit = body.get("limit", 100)
        
        logger.info(f"Searching memories with query={query}, filters={filters}, limit={limit}")
        
        # Get embedding for query
        embedding = memory.embedding_model.embed(query)
        
        # Search in Qdrant
        search_result = qdrant_client.search(
            collection_name="memories",
            query_vector=embedding,
            query_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="user_id",
                        match=models.MatchValue(value=filters.get("user_id"))
                    )
                ] + ([
                    models.FieldCondition(
                        key="agent_id",
                        match=models.MatchValue(value=filters.get("agent_id"))
                    )
                ] if filters.get("agent_id") else [])
            ),
            limit=limit
        )
        
        # Format results
        results = []
        seen_contents = set()  # Track seen memory contents to avoid duplicates
        for hit in search_result:
            content = hit.payload.get("content")
            if content not in seen_contents:
                seen_contents.add(content)
                results.append({
                    "id": hit.payload.get("id"),
                    "content": content,
                    "messages": hit.payload.get("messages", []),  # Include original messages
                    "metadata": {
                        "user_id": hit.payload.get("user_id"),
                        "agent_id": hit.payload.get("agent_id")
                    },
                    "score": hit.score
                })
        
        logger.info(f"Search result: {results}")
        return jsonify({"results": results})
        
    except Exception as e:
        logger.error(f"Error in search_memories: {str(e)}", exc_info=True)
        return jsonify({"message": str(e)}), 400

app.register_blueprint(api)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
