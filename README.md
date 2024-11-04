# Dockerized Mem0 REST APIs

This is an **unofficial** dockerized API server that wraps around Mem0's [open-source python project](https://github.com/mem0ai/mem0).

## Getting Started

This project requires an OpenAI API key to work. Support for other providers is not implemented yet.

First,

```bash
cp sample.env .env
```

Edit `.env` and replace the dummy value for `OPENAI_API_KEY` with an actual value. Then,

```bash
docker compose up
# The server is now running at http://localhost:4321
```

## Documentation

- [Integration Guide](docs/integration-guide.md) - Comprehensive guide for integrating this API into your projects
- [API Reference](docs/api-reference.md) - Detailed API endpoint documentation
- [Configuration Guide](docs/configuration.md) - Configuration options and environment setup

## Features

### Vector Database
The project uses Qdrant for vector storage and semantic search capabilities.

### Graph Database
The project now supports graph capabilities through Neo4j, allowing you to create and manage relationships between memories.

## Project Integration

For detailed instructions on integrating this API into your project, please refer to our [Integration Guide](docs/integration-guide.md). The guide covers:

- Installation & Setup
- Basic Integration Steps
- Authentication
- Core Features
- Advanced Usage
- Troubleshooting
- Performance Optimization

## API Examples

### Memory Operations

#### Add a memory

```bash
curl --request POST \
  --url http://localhost:4321/v1/memories/ \
  --header 'Content-Type: application/json' \
  --data '{
    "messages": [
      {
        "role": "user",
        "content": "I am working on improving my tennis skills. Suggest some online courses."
      }
    ],
    "user_id": "user1",
    "agent_id": "app1",
    "metadata": {"category": "hobbies"}
  }'
```

#### Update a memory

```bash
curl --request PUT \
  --url http://localhost:4321/v1/memories/<memory_id>/ \
  --header 'Content-Type: application/json' \
  --data '{"data": "Likes to play tennis on weekends"}'
```

#### Search for memories

```bash
curl --request POST \
 --url http://localhost:4321/v1/memories/search/ \
 --header 'Content-Type: application/json' \
 --data '{"query": "What are Alice'\''s hobbies?", "user_id": "user1"}'
```

#### Get all memories

```bash
curl http://localhost:4321/v1/memories/
```

#### Get a memory's history

```bash
curl http://localhost:4321/v1/memories/<memory_id>/history/
```

### Graph Operations

#### Create a relationship between memories

```bash
curl --request POST \
  --url http://localhost:4321/v1/relationships \
  --header 'Content-Type: application/json' \
  --data '{
    "source_id": "memory_id_1",
    "target_id": "memory_id_2",
    "type": "related_to",
    "weight": 0.8,
    "metadata": {"context": "sports_activities"}
  }'
```

#### Get relationships for a memory

```bash
curl --request GET \
  --url "http://localhost:4321/v1/memories/<memory_id>/relationships?type=related_to&min_weight=0.5"
```

#### Update a relationship

```bash
curl --request PUT \
  --url http://localhost:4321/v1/relationships/<relationship_id> \
  --header 'Content-Type: application/json' \
  --data '{
    "weight": 0.9,
    "metadata": {"updated_context": "high_priority"}
  }'
```

#### Delete a relationship

```bash
curl --request DELETE \
  --url http://localhost:4321/v1/relationships/<relationship_id>"
```

## API (dis)parity

We tried to keep it as close to [Mem0's cloud APIs](https://docs.mem0.ai/api-reference/overview) as possible, but there are still some differences between the API spec and the Python function calls. This shouldn't be treated as a 1:1 mapping of the cloud APIs, instead it is simply a wrapper over [the function calls](https://github.com/mem0ai/mem0/blob/main/mem0/memory/main.py#L27).

## Motivation

We are using Mem0 for our project at https://github.com/Airstrip-AI/airstrip (Typescript). In order to provide a fully open-source project, we need an API server i.e. "an open-source version of Mem0 cloud". We searched and did not find one, hence we built this.

If you are not building on Python, but want to try out Mem0 locally, hope this helps!
