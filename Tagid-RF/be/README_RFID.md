# RFID Tracking MVP - Backend System

Complete FastAPI backend system for RFID tracking MVP that integrates with the Chafon CF-H906 UHF handheld RFID reader.

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- PostgreSQL 12+
- CF-H906 UHF Handheld RFID Reader (optional for testing)

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd rfid-mvp-backend
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

5. **Access the API**
   - API Docs: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc
   - WebSocket: ws://localhost:8000/ws/rfid

## 📋 Features

- ✅ **PostgreSQL Database** - Stores RFID tags and scan history
- ✅ **REST API** - Full CRUD operations for tag management
- ✅ **WebSocket Server** - Real-time tag scan notifications
- ✅ **RFID Reader Integration** - Service for CF-H906 hardware
- ✅ **Tag Deduplication** - Automatic handling of duplicate EPCs
- ✅ **Complete Audit Trail** - Every scan recorded in history
- ✅ **Statistics API** - Tag counts, scan rates, location tracking

## 📚 API Documentation

### REST Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/tags` | Create/update tag |
| GET | `/api/v1/tags` | List tags (paginated, searchable) |
| GET | `/api/v1/tags/{id}` | Get tag by ID |
| GET | `/api/v1/tags/epc/{epc}` | Get tag by EPC |
| PUT | `/api/v1/tags/{id}` | Update tag metadata |
| DELETE | `/api/v1/tags/{id}` | Soft delete tag |
| GET | `/api/v1/tags/recent/scans` | Get recent scan history |
| GET | `/api/v1/tags/stats/summary` | Get statistics |

### WebSocket

- **Endpoint**: `ws://localhost:8000/ws/rfid`
- **Purpose**: Real-time tag scan notifications
- **Events**: `tag_scanned`, `welcome`, `pong`

## 🗄️ Database Schema

### `rfid_tags` Table
Master tag list with aggregated data:
- EPC (unique, indexed)
- TID, RSSI, antenna_port, frequency
- read_count, location, notes
- first_seen, last_seen timestamps

### `rfid_scan_history` Table
Complete audit trail:
- Every scan event recorded
- EPC, TID, RSSI, location, reader_id
- scanned_at timestamp (indexed)

## 🔧 Configuration

Edit `.env` file with your settings:

```env
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/rfid_mvp

# RFID Reader
RFID_READER_IP=192.168.1.100
RFID_READER_PORT=4001
RFID_CONNECTION_TYPE=wifi
RFID_READER_ID=CF-H906-001
```

## 📖 Full Documentation

See [RFID_README.md](./RFID_README.md) for complete documentation including:
- Hardware specifications
- Detailed API documentation
- Setup instructions
- Troubleshooting guide
- Development guide

## 🧪 Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

## 📦 Project Structure

```
be/
├── app/
│   ├── models/
│   │   └── rfid_tag.py          # SQLAlchemy models
│   ├── schemas/
│   │   └── rfid_tag.py          # Pydantic schemas
│   ├── routers/
│   │   ├── tags.py              # REST API endpoints
│   │   └── websocket.py         # WebSocket endpoint
│   ├── services/
│   │   ├── database.py          # SQLAlchemy setup
│   │   └── rfid_reader.py       # RFID reader service
│   └── utils/
│       └── helpers.py           # Utility functions
├── requirements.txt
├── .env.example
└── README.md
```

## 🔌 RFID Reader Integration

The RFID reader service supports three connection methods:
1. **chafon-rfid Python library** (if available)
2. **Direct TCP/IP socket** via WiFi
3. **Android app bridge** (POSTs to API)

See `app/services/rfid_reader.py` for implementation details.

## 📝 License

[Your License Here]

## 🤝 Contributing

[Your Contributing Guidelines Here]

## 📧 Support

For issues or questions, please open an issue on GitHub.

