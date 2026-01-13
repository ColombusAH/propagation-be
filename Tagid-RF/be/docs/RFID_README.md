# RFID Tracking MVP - Backend System

Complete backend system for RFID tracking MVP that integrates with the Chafon CF-H906 UHF handheld RFID reader.

## Overview

This system provides:
- **PostgreSQL database** for storing RFID tag data and scan history
- **REST API** for tag management and querying
- **WebSocket server** for real-time tag scan notifications
- **RFID reader integration** service for CF-H906 hardware

## Hardware Specifications

### CF-H906 UHF Handheld Reader
- **Model**: Chafon CF-H906
- **OS**: Android 9.0
- **Display**: 5.7 inch IPS HD screen
- **Battery**: 7000mAh
- **Reading Distance**: 0-20 meters (depends on tag and environment)
- **Reading Speed**: Up to 200 tags/second
- **Frequency**: 860-960MHz UHF
- **Connectivity**: WiFi, Bluetooth 4.0, 4G, USB
- **RAM/ROM**: 2GB+16GB (4GB+64GB optional)

### RFID Capabilities
- Supports ISO18000-6C (EPC Gen2) protocol
- Multi-tag reading with anti-collision
- Can read: EPC, TID, User Memory
- Provides RSSI (signal strength) data
- Configurable read power and region

## Project Structure

```
be/
├── app/
│   ├── models/
│   │   └── rfid_tag.py          # SQLAlchemy models (RFIDTag, RFIDScanHistory)
│   ├── schemas/
│   │   └── rfid_tag.py          # Pydantic schemas for validation
│   ├── routers/
│   │   ├── tags.py              # REST API endpoints for tags
│   │   └── websocket.py         # WebSocket endpoint for real-time updates
│   ├── services/
│   │   ├── database.py          # SQLAlchemy setup and session management
│   │   └── rfid_reader.py       # RFID reader integration service
│   └── utils/
│       └── helpers.py           # Utility functions
├── .env.example                 # Environment variables template
└── requirements.txt            # Python dependencies
```

## Database Models

### `rfid_tags` Table
Master tag list with aggregated data:
- **id**: Primary key (auto-increment)
- **epc**: Electronic Product Code (unique, indexed, max 128 chars) - REQUIRED
- **tid**: Tag ID (indexed, max 128 chars, optional)
- **user_memory**: User-defined data (optional)
- **rssi**: Signal strength in dBm (float)
- **antenna_port**: Antenna number (1-4)
- **read_count**: Number of times scanned (default: 1)
- **frequency**: Operating frequency in MHz (float)
- **pc**: Protocol Control bits (string, max 16 chars)
- **crc**: Cyclic Redundancy Check (string, max 16 chars)
- **metadata**: JSON field for additional data
- **location**: Physical location (string, max 100 chars)
- **notes**: User notes (string, max 500 chars)
- **is_active**: Boolean flag for soft delete (default: true)
- **first_seen**: Timestamp of first scan (auto)
- **last_seen**: Timestamp of most recent scan (auto-update)
- **created_at**: Record creation timestamp
- **updated_at**: Record update timestamp

### `rfid_scan_history` Table
Complete audit trail of all scan events:
- **id**: Primary key
- **epc**: Tag EPC (indexed)
- **tid**: Tag ID
- **rssi**: Signal strength at scan time
- **antenna_port**: Antenna that detected
- **frequency**: Frequency used
- **location**: Location at scan time
- **reader_id**: Identifier of the reader device
- **metadata**: JSON for additional scan context
- **scanned_at**: Scan timestamp (indexed)

**Important**: Every scan creates a new entry in `rfid_scan_history`, even if the tag already exists in `rfid_tags`.

## API Endpoints

### REST API (`/api/v1/tags`)

#### POST `/api/v1/tags`
Create or update a tag. If EPC exists, updates the existing record (increments `read_count`, updates `last_seen`).

**Request Body:**
```json
{
  "epc": "E200001234567890ABCDEF01",
  "tid": "E280001234567890ABCDEF01",
  "rssi": -45.5,
  "antenna_port": 1,
  "frequency": 920.5,
  "location": "Warehouse A",
  "metadata": {"batch": "2024-001"}
}
```

#### GET `/api/v1/tags`
List all tags with pagination.

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 50, max: 100)
- `search`: Search by EPC or TID
- `is_active`: Filter by active status (true/false)

**Example:**
```
GET /api/v1/tags?page=1&page_size=50&search=E200&is_active=true
```

#### GET `/api/v1/tags/{id}`
Get a specific tag by ID.

#### GET `/api/v1/tags/epc/{epc}`
Get a tag by EPC.

#### PUT `/api/v1/tags/{id}`
Update tag metadata (location, notes, etc.). Does NOT increment `read_count`.

**Request Body:**
```json
{
  "location": "Warehouse B",
  "notes": "Moved to new location",
  "is_active": true
}
```

#### DELETE `/api/v1/tags/{id}`
Soft delete a tag (sets `is_active=false`).

#### GET `/api/v1/tags/recent/scans`
Get recent scan history.

**Query Parameters:**
- `hours`: Hours to look back (default: 24, max: 168)
- `limit`: Maximum results (default: 100, max: 1000)

**Example:**
```
GET /api/v1/tags/recent/scans?hours=24&limit=100
```

#### GET `/api/v1/tags/stats/summary`
Get tag statistics:
- Total tags
- Active tags
- Scans today
- Scans last hour
- Most scanned tag
- Average RSSI
- Tags by location

### WebSocket (`/ws/rfid`)

Connect to WebSocket for real-time tag scan notifications.

**JavaScript Example:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/rfid');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'tag_scanned') {
    console.log('Tag scanned:', data.data);
  }
};

// Send ping
ws.send(JSON.stringify({ command: 'ping', timestamp: Date.now() }));
```

**Message Types:**
- `welcome`: Sent on connection
- `tag_scanned`: Real-time tag scan event
- `pong`: Response to ping
- `error`: Error message

## Setup Instructions

### 1. Install Dependencies

```bash
cd be
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and update the values:

```bash
cp .env.example .env
```

Edit `.env` with your settings:
- `DATABASE_URL`: PostgreSQL connection string
- `RFID_READER_IP`: CF-H906 WiFi IP address (default: 192.168.1.100)
- `RFID_READER_PORT`: RFID reader port (default: 4001)
- `RFID_CONNECTION_TYPE`: Connection type (wifi/bluetooth/serial)
- `RFID_READER_ID`: Unique identifier for this reader

### 3. Initialize Database

The database tables are automatically created on application startup. Alternatively, you can run:

```python
from app.services.database import init_db
init_db()
```

### 4. Run the Application

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **WebSocket**: ws://localhost:8000/ws/rfid

## RFID Reader Integration

### Connection Options

The system supports three methods for connecting to the CF-H906:

#### Option 1: chafon-rfid Python Library (Preferred)
If available on PyPI or GitHub, install:
```bash
pip install chafon-rfid
# or
pip install git+https://github.com/wabson/chafon-rfid.git
```

Then uncomment the library usage in `app/services/rfid_reader.py`.

#### Option 2: Direct TCP/IP Socket Connection
The service uses direct TCP/IP socket connection via WiFi by default. Ensure:
- CF-H906 is connected to WiFi
- IP address is configured correctly in `.env`
- Reader is accessible on the network

#### Option 3: Android App Bridge
Create a lightweight Android app on the CF-H906 that:
- Uses the official Chafon Android SDK
- Scans tags continuously
- POSTs tag data to `/api/v1/tags` endpoint

### Starting Scanning

The RFID reader service can be started manually or automatically on startup.

**Manual:**
```python
from app.services.rfid_reader import rfid_reader_service

# Connect
await rfid_reader_service.connect()

# Start scanning
await rfid_reader_service.start_scanning()

# Stop scanning
await rfid_reader_service.stop_scanning()

# Disconnect
await rfid_reader_service.disconnect()
```

**Automatic (on startup):**
Uncomment the auto-connect code in `app/main.py` lifespan function.

## Data Flow

```
CF-H906 Reader
    ↓ (WiFi/Bluetooth)
Python RFID Service
    ↓
Parse Tag Data (EPC, TID, RSSI, etc.)
    ↓
    ├─→ Save to PostgreSQL (upsert tags + insert history)
    ├─→ Broadcast via WebSocket (real-time to React)
    └─→ Call callback function (if provided)
```

## Tag Deduplication

When a tag is scanned:
1. System checks if EPC exists in `rfid_tags` table
2. If exists: Updates existing record (increments `read_count`, updates `last_seen`)
3. If new: Creates new tag record
4. **Always**: Creates new entry in `rfid_scan_history` (full audit trail)

## Testing

### Manual API Testing

**Create/Update Tag:**
```bash
curl -X POST "http://localhost:8000/api/v1/tags" \
  -H "Content-Type: application/json" \
  -d '{
    "epc": "E200001234567890ABCDEF01",
    "rssi": -45.5,
    "antenna_port": 1,
    "frequency": 920.5,
    "location": "Warehouse A"
  }'
```

**List Tags:**
```bash
curl "http://localhost:8000/api/v1/tags?page=1&page_size=50"
```

**Get Statistics:**
```bash
curl "http://localhost:8000/api/v1/tags/stats/summary"
```

**Get Recent Scans:**
```bash
curl "http://localhost:8000/api/v1/tags/recent/scans?hours=24"
```

### WebSocket Testing

Use a WebSocket client or browser console:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/rfid');
ws.onopen = () => console.log('Connected');
ws.onmessage = (e) => console.log(JSON.parse(e.data));
ws.send(JSON.stringify({ command: 'ping' }));
```

## Performance Targets

- API response time: <100ms for most endpoints
- WebSocket latency: <50ms for broadcasts
- Tag scanning: Support 50-200 tags/second (CF-H906 capability)
- Database: Efficiently handle millions of scan records
- Concurrent WebSocket connections: 100+

## Security Considerations (MVP)

- CORS properly configured for frontend origins
- Input validation via Pydantic schemas
- SQL injection protection (SQLAlchemy ORM)
- Environment variables for sensitive config

For production (future phases):
- JWT authentication
- API rate limiting
- HTTPS/WSS only
- Role-based access control

## Logging

Logs are configured at different levels:
- **INFO**: Normal operations, connections, scans
- **WARNING**: Recoverable errors, retries
- **ERROR**: Failed operations, exceptions
- **DEBUG**: Detailed tag data, SQL queries (when DEBUG=True)

Set `LOG_LEVEL` in `.env` to control logging verbosity.

## Troubleshooting

### Database Connection Issues
- Verify `DATABASE_URL` is correct
- Ensure PostgreSQL is running
- Check network connectivity

### RFID Reader Connection Issues
- Verify CF-H906 is on same network (WiFi mode)
- Check IP address and port in `.env`
- Test connectivity: `ping <RFID_READER_IP>`
- Review logs for connection errors

### WebSocket Connection Issues
- Ensure WebSocket endpoint is accessible
- Check CORS settings for frontend origin
- Verify firewall allows WebSocket connections

## Development

### Adding New Features

1. **Database Models**: Add to `app/models/rfid_tag.py`
2. **Schemas**: Add to `app/schemas/rfid_tag.py`
3. **Endpoints**: Add to `app/routers/tags.py`
4. **Services**: Add to `app/services/rfid_reader.py`

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

## TODO / Future Enhancements

- [ ] Implement actual CF-H906 hardware integration (currently skeleton)
- [ ] Add unit tests for all endpoints
- [ ] Add integration tests for RFID reader service
- [ ] Implement tag writing functionality
- [ ] Add batch tag import/export
- [ ] Add tag filtering and advanced search
- [ ] Implement tag grouping/categories
- [ ] Add user authentication and authorization
- [ ] Add API rate limiting
- [ ] Implement tag alerts/notifications
- [ ] Add data export (CSV, JSON)
- [ ] Implement tag analytics dashboard

## Support

For issues or questions:
1. Check the logs in `logs/app.log`
2. Review API documentation at `/docs`
3. Check RFID reader connection settings
4. Verify database connectivity

## License

[Add your license here]


