# Memory System API Documentation

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

All endpoints require JWT authentication. Include the token in the Authorization header:

```
Authorization: Bearer <token>
```

## Endpoints

### Memory Operations

#### Create Memory
```http
POST /memories
Content-Type: application/json

{
    "content": "Memory content",
    "type": "memory",
    "level": 1,
    "importance": 0.5,
    "metadata": {
        "user_id": "user123",
        "tags": ["tag1", "tag2"]
    }
}

Response 200:
{
    "id": "memory123",
    "content": "Memory content",
    "metadata": {
        "type": "memory",
        "level": 1,
        "importance": 0.5,
        "created_at": "2023-01-01T00:00:00Z",
        "user_id": "user123",
        "tags": ["tag1", "tag2"]
    }
}
```

#### Get Memory
```http
GET /memories/{memory_id}

Response 200:
{
    "id": "memory123",
    "content": "Memory content",
    "metadata": {
        "type": "memory",
        "level": 1,
        "importance": 0.5,
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": null,
        "user_id": "user123"
    }
}
```

#### Update Memory
```http
PUT /memories/{memory_id}
Content-Type: application/json

{
    "content": "Updated content",
    "type": "updated",
    "level": 2,
    "importance": 0.8
}

Response 200:
{
    "id": "memory123",
    "content": "Updated content",
    "metadata": {
        "type": "updated",
        "level": 2,
        "importance": 0.8,
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-02T00:00:00Z",
        "user_id": "user123"
    }
}
```

#### Delete Memory
```http
DELETE /memories/{memory_id}

Response 200:
{
    "success": true,
    "message": "Memory deleted successfully"
}
```

#### List Memories
```http
GET /memories?type=memory&level=1&importance=0.5&page=1&limit=10

Response 200:
{
    "results": [
        {
            "id": "memory123",
            "content": "Memory content",
            "metadata": {...}
        }
    ],
    "total": 100,
    "page": 1,
    "limit": 10,
    "has_more": true
}
```

### Memory Search

#### Search Memories
```http
POST /queries/search
Content-Type: application/json

{
    "query": "search term",
    "filters": {
        "type": "memory",
        "level": 1,
        "importance": 0.5,
        "start_date": "2023-01-01",
        "end_date": "2023-12-31"
    },
    "page": 1,
    "limit": 10
}

Response 200:
{
    "results": [
        {
            "id": "memory123",
            "content": "Memory content",
            "metadata": {...},
            "score": 0.95
        }
    ],
    "total": 50,
    "page": 1,
    "limit": 10,
    "has_more": true
}
```

#### Get Similar Memories
```http
GET /queries/similar/{memory_id}?limit=10

Response 200:
{
    "results": [
        {
            "id": "memory456",
            "content": "Similar content",
            "metadata": {...},
            "similarity": 0.85
        }
    ]
}
```

### Memory History

#### Get Memory History
```http
GET /history/{memory_id}

Response 200:
{
    "memory_id": "memory123",
    "history": [
        {
            "action": "create",
            "timestamp": "2023-01-01T00:00:00Z",
            "changes": {...},
            "user_id": "user123"
        },
        {
            "action": "update",
            "timestamp": "2023-01-02T00:00:00Z",
            "changes": {...},
            "user_id": "user123"
        }
    ]
}
```

#### Get Memory Relations
```http
GET /history/relations/{memory_id}

Response 200:
{
    "memory_id": "memory123",
    "relations": [
        {
            "id": "relation123",
            "source_id": "memory123",
            "target_id": "memory456",
            "type": "reference",
            "metadata": {...},
            "created_at": "2023-01-01T00:00:00Z"
        }
    ]
}
```

### WebSocket Endpoints

#### Memory Updates Stream
```websocket
WS /ws/memory/{session_id}?token={jwt_token}

// Connect message
{
    "type": "connect",
    "session_id": "session123",
    "user_id": "user123"
}

// Memory update message
{
    "type": "memory_update",
    "data": {
        "id": "memory123",
        "content": "Updated content",
        "metadata": {...}
    }
}

// Memory stream message
{
    "type": "stream",
    "data": {
        "content": "Streamed content",
        "chunk_size": 100,
        "done": false
    }
}
```

### Batch Operations

#### Batch Update Memories
```http
POST /memories/batch
Content-Type: application/json

{
    "operation": "update",
    "memories": [
        {
            "id": "memory123",
            "content": "Updated content 1",
            "metadata": {...}
        },
        {
            "id": "memory456",
            "content": "Updated content 2",
            "metadata": {...}
        }
    ]
}

Response 200:
{
    "successful": ["memory123", "memory456"],
    "failed": [],
    "metadata": {
        "total": 2,
        "success": 2,
        "failed": 0
    }
}
```

### Error Responses

#### 400 Bad Request
```json
{
    "error": "validation_error",
    "message": "Invalid request parameters",
    "details": {
        "field": ["error message"]
    }
}
```

#### 401 Unauthorized
```json
{
    "error": "unauthorized",
    "message": "Invalid or expired token"
}
```

#### 403 Forbidden
```json
{
    "error": "forbidden",
    "message": "Insufficient permissions"
}
```

#### 404 Not Found
```json
{
    "error": "not_found",
    "message": "Memory not found"
}
```

#### 429 Too Many Requests
```json
{
    "error": "rate_limit_exceeded",
    "message": "Too many requests",
    "retry_after": 60
}
```

#### 500 Internal Server Error
```json
{
    "error": "internal_server_error",
    "message": "An unexpected error occurred",
    "request_id": "req123"
}
```

## Rate Limits

- HTTP endpoints: 1000 requests per minute per user
- WebSocket messages: 500 messages per minute per connection
- Batch operations: 100 items per request
- Search queries: 100 requests per minute per user

## Pagination

All list endpoints support pagination with the following parameters:

- `page`: Page number (default: 1)
- `limit`: Items per page (default: 10, max: 100)
- `cursor`: Cursor for cursor-based pagination

Response includes:
- `total`: Total number of items
- `has_more`: Boolean indicating more pages
- `next_cursor`: Cursor for next page

## Filtering

Common filter parameters:

- `type`: Memory type
- `level`: Memory importance level (1-10)
- `importance`: Memory importance score (0.0-1.0)
- `start_date`: Start date for date range
- `end_date`: End date for date range
- `user_id`: Filter by user ID
- `tags`: Array of tags to filter by

## Sorting

Use `sort` parameter with the following values:

- `created_at:asc/desc`
- `updated_at:asc/desc`
- `importance:asc/desc`
- `level:asc/desc`
- `relevance` (for search results)

## Versioning

API versioning is handled through the URL path:
- Current version: `/api/v1`
- Legacy version: `/api/v0` (deprecated)
- Beta features: `/api/v1-beta`
