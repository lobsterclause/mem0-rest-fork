# Memory System REST API

A FastAPI-based REST API for memory operations, providing a robust interface for managing and querying memories.

## Features

- Memory CRUD operations
- Memory search and querying
- Memory history tracking
- Memory relations management
- Real-time updates via WebSocket
- Cross-session memory bridging
- Memory compression
- Memory suggestions

## Requirements

- Python 3.9+
- Docker and Docker Compose
- Neo4j 4.4+
- Qdrant latest version
- OpenAI API key

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/yourusername/mem0-rest.git
cd mem0-rest
```

2. Copy the sample environment file and update it with your settings:
```bash
cp sample.env .env
```

3. Start the services using Docker Compose:
```bash
docker-compose up -d
```

4. The API will be available at http://localhost:8000
   - API documentation: http://localhost:8000/api/docs
   - ReDoc documentation: http://localhost:8000/api/redoc

## Development Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
.\venv\Scripts\activate   # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the development server:
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Memory Operations
- `POST /api/memories/` - Create a new memory
- `GET /api/memories/{memory_id}` - Get a memory by ID
- `PUT /api/memories/{memory_id}` - Update a memory
- `DELETE /api/memories/{memory_id}` - Delete a memory
- `GET /api/memories/` - List memories with filters

### Memory Search
- `POST /api/queries/search` - Search memories
- `GET /api/queries/suggestions` - Get memory suggestions
- `GET /api/queries/similar/{memory_id}` - Get similar memories

### Memory History
- `GET /api/history/{memory_id}` - Get memory history
- `GET /api/history/relations/{memory_id}` - Get memory relations
- `POST /api/history/relations` - Add memory relation
- `DELETE /api/history/relations/{relation_id}` - Remove memory relation

### WebSocket Endpoints
- `/api/ws/memory/{session_id}` - Memory updates stream
- `/api/ws/stream/{session_id}` - Memory content stream

## Configuration

The application can be configured using environment variables or a `.env` file. See `sample.env` for available options.

### Key Configuration Options

- `API_VERSION` - API version
- `DEBUG` - Enable debug mode
- `JWT_SECRET` - Secret key for JWT tokens
- `OPENAI_API_KEY` - OpenAI API key
- `QDRANT_HOST` - Qdrant host
- `NEO4J_URI` - Neo4j connection URI

## Testing

Run tests using pytest:
```bash
pytest
```

Run tests with coverage:
```bash
pytest --cov=src --cov-report=html
```

## Docker Support

Build the Docker image:
```bash
docker build -t mem0-rest .
```

Run the container:
```bash
docker run -p 8000:8000 --env-file .env mem0-rest
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
