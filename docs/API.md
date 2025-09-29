# HackSeek API Documentation

This document provides an overview of the HackSeek REST API endpoints.

## Base URL

- Development: `http://localhost:8000`
- Production: `https://api.hackseek.com` (when deployed)

## Authentication

The API uses JWT tokens for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## Common Response Format

All API responses follow this structure:

```json
{
  "success": true,
  "data": {...},
  "message": "Operation successful",
  "timestamp": "2025-01-01T12:00:00Z"
}
```

Error responses:
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {...}
  },
  "timestamp": "2025-01-01T12:00:00Z"
}
```

## Endpoints

### Health Check

#### GET /health
Check API status and service health.

**Response:**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "version": "0.1.0",
    "services": {
      "database": "connected",
      "redis": "connected"
    }
  }
}
```

### Authentication

#### POST /api/auth/register
Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid-string",
      "email": "user@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "is_verified": false
    },
    "access_token": "jwt-token-string"
  }
}
```

#### POST /api/auth/login
Authenticate user and get access token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user": {...},
    "access_token": "jwt-token-string",
    "expires_in": 86400
  }
}
```

#### POST /api/auth/refresh
Refresh access token.

**Headers:**
```
Authorization: Bearer <current-token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "access_token": "new-jwt-token",
    "expires_in": 86400
  }
}
```

### Hackathons

#### GET /api/hackathons
Search and filter hackathons.

**Query Parameters:**
- `q` (string): Search query
- `location` (string): Location filter
- `start_date` (string): Start date filter (ISO 8601)
- `end_date` (string): End date filter (ISO 8601)
- `categories` (array): Category filters
- `technologies` (array): Technology filters
- `difficulty_level` (string): Difficulty filter
- `is_online` (boolean): Online event filter
- `min_prize` (number): Minimum prize money
- `page` (number): Page number (default: 1)
- `limit` (number): Results per page (default: 20, max: 100)
- `sort` (string): Sort by ('start_date', 'prize_money', 'created_at')
- `order` (string): Sort order ('asc', 'desc')

**Example Request:**
```
GET /api/hackathons?q=AI&location=online&min_prize=1000&page=1&limit=20
```

**Response:**
```json
{
  "success": true,
  "data": {
    "hackathons": [
      {
        "id": "uuid-string",
        "title": "AI Innovation Challenge",
        "description": "Build innovative AI solutions...",
        "short_description": "AI hackathon for developers",
        "organizer": "TechCorp",
        "website_url": "https://example.com",
        "registration_url": "https://example.com/register",
        "image_url": "https://example.com/image.jpg",
        "start_date": "2025-02-01T09:00:00Z",
        "end_date": "2025-02-03T18:00:00Z",
        "registration_deadline": "2025-01-25T23:59:59Z",
        "location": "Online",
        "is_online": true,
        "is_hybrid": false,
        "participation_fee": 0,
        "prize_money": 10000,
        "max_participants": 500,
        "difficulty_level": "Intermediate",
        "categories": ["AI", "Machine Learning"],
        "technologies": ["Python", "TensorFlow", "React"],
        "source_platform": "devpost",
        "is_active": true,
        "created_at": "2025-01-01T12:00:00Z",
        "updated_at": "2025-01-01T12:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 150,
      "pages": 8,
      "has_next": true,
      "has_prev": false
    },
    "filters_applied": {
      "query": "AI",
      "location": "online",
      "min_prize": 1000
    }
  }
}
```

#### GET /api/hackathons/{hackathon_id}
Get detailed information about a specific hackathon.

**Response:**
```json
{
  "success": true,
  "data": {
    "hackathon": {
      "id": "uuid-string",
      "title": "AI Innovation Challenge",
      // ... full hackathon details
      "related_hackathons": [
        // Similar hackathons
      ]
    }
  }
}
```

### User Favorites

#### GET /api/users/favorites
Get user's favorite hackathons.

**Headers:**
```
Authorization: Bearer <jwt-token>
```

**Query Parameters:**
- `page` (number): Page number
- `limit` (number): Results per page

**Response:**
```json
{
  "success": true,
  "data": {
    "favorites": [
      {
        "id": "favorite-uuid",
        "hackathon": {
          // Full hackathon object
        },
        "created_at": "2025-01-01T12:00:00Z"
      }
    ],
    "pagination": {...}
  }
}
```

#### POST /api/users/favorites
Add hackathon to favorites.

**Headers:**
```
Authorization: Bearer <jwt-token>
```

**Request Body:**
```json
{
  "hackathon_id": "hackathon-uuid-string"
}
```

#### DELETE /api/users/favorites/{hackathon_id}
Remove hackathon from favorites.

**Headers:**
```
Authorization: Bearer <jwt-token>
```

### AI Chat

#### POST /api/chat/sessions
Create new chat session.

**Request Body:**
```json
{
  "user_id": "user-uuid-string" // Optional for anonymous users
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "session": {
      "id": "session-uuid",
      "session_token": "session-token-string",
      "user_id": "user-uuid-string",
      "is_active": true,
      "created_at": "2025-01-01T12:00:00Z"
    }
  }
}
```

#### POST /api/chat/sessions/{session_id}/messages
Send message to AI chatbot.

**Request Body:**
```json
{
  "message": "Find me AI hackathons in January 2025 with prizes over $5000",
  "context": {
    "user_preferences": {
      "location": "online",
      "skill_level": "intermediate"
    }
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "message": {
      "id": "message-uuid",
      "session_id": "session-uuid",
      "message_type": "assistant",
      "content": "I found 12 AI hackathons matching your criteria...",
      "metadata": {
        "recommended_hackathons": [
          // Array of hackathon objects
        ],
        "search_filters": {
          "categories": ["AI"],
          "min_prize": 5000,
          "start_date": "2025-01-01",
          "end_date": "2025-01-31"
        }
      },
      "created_at": "2025-01-01T12:00:00Z"
    }
  }
}
```

#### GET /api/chat/sessions/{session_id}/messages
Get chat conversation history.

**Query Parameters:**
- `limit` (number): Number of messages to retrieve
- `before` (string): Get messages before this message ID

**Response:**
```json
{
  "success": true,
  "data": {
    "messages": [
      {
        "id": "message-uuid",
        "message_type": "user",
        "content": "Find me hackathons",
        "created_at": "2025-01-01T12:00:00Z"
      },
      {
        "id": "message-uuid",
        "message_type": "assistant",
        "content": "Here are some great hackathons...",
        "metadata": {...},
        "created_at": "2025-01-01T12:01:00Z"
      }
    ]
  }
}
```

### Analytics

#### POST /api/analytics/search
Log search activity for analytics.

**Request Body:**
```json
{
  "search_query": "AI hackathons",
  "search_filters": {
    "location": "online",
    "categories": ["AI"]
  },
  "results_count": 25,
  "session_id": "session-uuid",
  "clicked_hackathon_id": "hackathon-uuid" // Optional
}
```

## Error Codes

| Code | Description |
|------|-------------|
| `VALIDATION_ERROR` | Request validation failed |
| `AUTHENTICATION_REQUIRED` | Valid JWT token required |
| `UNAUTHORIZED` | Insufficient permissions |
| `NOT_FOUND` | Resource not found |
| `DUPLICATE_ENTRY` | Resource already exists |
| `RATE_LIMIT_EXCEEDED` | Too many requests |
| `EXTERNAL_API_ERROR` | External service error |
| `DATABASE_ERROR` | Database operation failed |
| `INTERNAL_ERROR` | Internal server error |

## Rate Limiting

The API implements rate limiting to ensure fair usage:

- **Anonymous users**: 100 requests per hour
- **Authenticated users**: 1000 requests per hour
- **Search endpoints**: Additional limits may apply

Rate limit headers:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

## SDKs and Client Libraries

Official client libraries (planned):
- JavaScript/TypeScript
- Python
- Go
- Java

## Webhook Events

Webhook support for real-time updates (planned):
- New hackathons added
- Hackathon details updated
- Registration deadlines approaching
- User favorite hackathon updates

## Versioning

The API uses semantic versioning. Current version: v1

All endpoints are prefixed with the version: `/api/v1/`

Previous versions will be supported for at least 6 months after a new version is released.