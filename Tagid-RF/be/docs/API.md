# API Documentation

## Base URL
`http://localhost:8000/api/v1`

## Authentication

### Google OAuth Login
**POST** `/auth/google`

Request:
```json
{"token": "google-oauth-id-token"}
```

Response:
```json
{
  "message": "Login successful",
  "user_id": "uuid",
  "role": "USER",
  "token": "jwt-token"
}
```

### Get Current User
**GET** `/auth/me`

Headers: `Authorization: Bearer <jwt-token>`

## Tags (RFID)

### List Tags
**GET** `/tags/`

Query params: `skip`, `limit`, `location`

### Get Tag by EPC
**GET** `/tags/{epc}`

### Create/Update Tag
**POST** `/tags/`

Request:
```json
{
  "epc": "E200ABCD1234",
  "tid": "optional",
  "rssi": -45.5,
  "location": "Warehouse-A"
}
```

### Get Tag Stats
**GET** `/tags/stats`

Response:
```json
{
  "total_tags": 150,
  "tags_by_location": {...}
}
```

## WebSocket

### RFID Real-time Updates
**WS** `/ws/rfid`

Messages:
```json
{"type": "tag_scanned", "data": {...}}
{"type": "welcome", "message": "Connected"}
```

Commands:
```json
{"command": "ping"} → {"type": "pong"}
{"command": "subscribe"} → {"type": "subscribed"}
```

## Health Checks

- **GET** `/health` - Service health
- **GET** `/healthz` - Kubernetes probe
