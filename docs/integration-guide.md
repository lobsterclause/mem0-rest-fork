# Integration Guide for Mem0 REST APIs

This guide will help you integrate the Mem0 REST APIs into your project. This service provides a REST API wrapper around Mem0's core functionality, offering memory storage, semantic search, and graph relationship capabilities.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Basic Integration](#basic-integration)
- [Authentication](#authentication)
- [Core Features](#core-features)
- [Advanced Usage](#advanced-usage)
- [Troubleshooting](#troubleshooting)

## Prerequisites

- Docker and Docker Compose installed on your system
- An OpenAI API key
- Basic understanding of REST APIs
- Storage requirements:
  - At least 1GB of free disk space for Docker images
  - Additional space for vector and graph databases

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/mem0-rest-fork.git
cd mem0-rest-fork
```

2. Set up environment variables:
```bash
cp sample.env .env
```

3. Edit `.env` file with your configuration:
```env
OPENAI_API_KEY=your_openai_api_key
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
QDRANT_HOST=qdrant
QDRANT_PORT=6333
```

4. Start the services:
```bash
docker compose up
```

The API server will be available at `http://localhost:4321`.

## Basic Integration

### Making Your First Request

Here's a simple example in Python:

```python
import requests

API_BASE_URL = "http://localhost:4321/v1"

# Add a memory
response = requests.post(
    f"{API_BASE_URL}/memories/",
    json={
        "messages": [
            {
                "role": "user",
                "content": "Important meeting with client on Monday at 10 AM"
            }
        ],
        "user_id": "user123",
        "agent_id": "app1",
        "metadata": {"category": "meetings"}
    }
)

memory_id = response.json()["id"]
```

### Core API Endpoints

1. Memory Operations:
   - POST `/v1/memories/` - Create a memory
   - GET `/v1/memories/` - List all memories
   - GET `/v1/memories/{memory_id}/` - Get specific memory
   - PUT `/v1/memories/{memory_id}/` - Update memory
   - DELETE `/v1/memories/{memory_id}/` - Delete memory
   - POST `/v1/memories/search/` - Search memories

2. Graph Operations:
   - POST `/v1/relationships` - Create relationship
   - GET `/v1/memories/{memory_id}/relationships` - Get relationships
   - PUT `/v1/relationships/{relationship_id}` - Update relationship
   - DELETE `/v1/relationships/{relationship_id}` - Delete relationship

## Authentication

Currently, the API uses API keys for authentication. Include your OpenAI API key in the `.env` file. Future versions may include additional authentication methods.

## Core Features

### 1. Memory Management

```python
# Create a memory
def create_memory(content, user_id, agent_id, metadata=None):
    return requests.post(
        f"{API_BASE_URL}/memories/",
        json={
            "messages": [{"role": "user", "content": content}],
            "user_id": user_id,
            "agent_id": agent_id,
            "metadata": metadata or {}
        }
    ).json()

# Search memories
def search_memories(query, user_id):
    return requests.post(
        f"{API_BASE_URL}/memories/search/",
        json={
            "query": query,
            "user_id": user_id
        }
    ).json()
```

### 2. Graph Relationships

```python
# Create a relationship
def create_relationship(source_id, target_id, rel_type, weight=0.8, metadata=None):
    return requests.post(
        f"{API_BASE_URL}/relationships",
        json={
            "source_id": source_id,
            "target_id": target_id,
            "type": rel_type,
            "weight": weight,
            "metadata": metadata or {}
        }
    ).json()

# Get relationships for a memory
def get_relationships(memory_id, rel_type=None, min_weight=0.0):
    params = {"type": rel_type, "min_weight": min_weight} if rel_type else {}
    return requests.get(
        f"{API_BASE_URL}/memories/{memory_id}/relationships",
        params=params
    ).json()
```

## Advanced Usage

### 1. Batch Operations

For better performance when dealing with multiple memories:

```python
def batch_create_memories(memories):
    results = []
    for memory in memories:
        response = requests.post(
            f"{API_BASE_URL}/memories/",
            json=memory
        )
        results.append(response.json())
    return results
```

### 2. Complex Graph Queries

```python
def find_related_memories(memory_id, depth=2, min_weight=0.5):
    """Find memories related up to a certain depth with minimum weight"""
    related = set()
    to_process = {memory_id}
    
    for _ in range(depth):
        current_batch = to_process.copy()
        to_process.clear()
        
        for mid in current_batch:
            relationships = get_relationships(mid, min_weight=min_weight)
            for rel in relationships:
                target_id = rel["target_id"]
                if target_id not in related:
                    related.add(target_id)
                    to_process.add(target_id)
    
    return list(related)
```

## Troubleshooting

### Common Issues

1. Connection Refused
   - Ensure Docker containers are running
   - Check if port 4321 is available
   - Verify network settings in docker-compose.yml

2. Authentication Errors
   - Verify OpenAI API key in .env
   - Check API key permissions

3. Memory Creation Fails
   - Ensure proper JSON format
   - Verify required fields (messages, user_id, agent_id)
   - Check message content length

4. Search Not Working
   - Verify vector database (Qdrant) is running
   - Check memory embeddings generation
   - Ensure proper search query format

### Debugging Tips

1. Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

2. Check container logs:
```bash
docker compose logs -f
```

3. Verify service health:
```bash
curl http://localhost:4321/health
```

### Performance Optimization

1. Connection Pooling:
```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()
retry = Retry(total=3, backoff_factor=0.1)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
```

2. Batch Processing:
- Group related operations
- Use bulk endpoints when available
- Implement rate limiting for large batches

## Support

For issues and feature requests, please:
1. Check the GitHub issues page
2. Review existing documentation
3. Create a new issue with detailed information

Remember to include:
- API version
- Request/response details
- Error messages
- Environment details
