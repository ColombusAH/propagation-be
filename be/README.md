# Shifty Backend

Backend service for Shifty application.

## Database Management

This project uses Prisma ORM with PostgreSQL. Here's how to manage your database:

### Local Development

For local development, we have a Python script that handles database operations:

```bash
# Generate Prisma client (run after schema changes)
python scripts/db.py generate

# Create a new migration (after changing schema.prisma)
python scripts/db.py migrate --name migration_name

# Deploy all pending migrations
python scripts/db.py deploy

# Check migration status
python scripts/db.py status

# Reset database (WARNING: destroys all data)
python scripts/db.py reset
```

### Docker Environment

When running in Docker, migrations are automatically applied at startup via the `docker-entrypoint.sh` script. 

To run the application in Docker:

```bash
# Build and start the containers
docker-compose up -d

# View logs
docker-compose logs -f

# Run manual migrations (if needed)
docker-compose exec api npx prisma migrate deploy

# Generate client (if needed)
docker-compose exec api npx prisma generate

# Reset database (WARNING: destroys all data)
docker-compose exec api npx prisma migrate reset --force
```

## Running the Application

### Local Development

1. Make sure PostgreSQL is running locally on port 5432
2. Create a `.env` file with DATABASE_URL and SECRET_KEY
3. Run the application:

```bash
# Generate Prisma client
python scripts/db.py generate

# Apply migrations
python scripts/db.py deploy

# Start the application
uvicorn app.main:app --reload
```

### Docker Environment

```bash
# Start all services
docker-compose up -d

# Access API at http://localhost:8000
```

## Railway Deployment

This project is configured for easy deployment to [Railway](https://railway.app).

### Automatic Deployment

1. Create a new project in Railway
2. Connect your GitHub repository
3. Add a PostgreSQL database service from the Railway dashboard
4. Deploy the app - Railway will automatically:
   - Use the Dockerfile to build the application
   - Connect the PostgreSQL database
   - Set up environment variables
   - Run database migrations

### Manual Deployment

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Link to your project
railway link

# Deploy application
railway up
```

### Environment Variables

Railway will automatically provide the following environment variables:

- `DATABASE_URL`: Connection string for your PostgreSQL database
- `PORT`: The port Railway will expose your application on

You should add these additional variables in the Railway dashboard:

- `SECRET_KEY`: A secret key for securing your application

## API Documentation

When the application is running, you can access the API documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc 

run locally :
create env if not exists:
python3 -m venv .venv  
activate env :
source .venv/bin/activate

## Testing

This project uses pytest with 91% code coverage.

### Running Tests

```bash
# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Run all tests with coverage
pytest --cov=app --cov-report=term-missing

# Run specific test file
pytest tests/api/v1/test_auth.py -v

# Run with verbose output
pytest -v -s
```

### Test Structure

```
tests/
├── api/v1/           # API endpoint tests
│   ├── test_auth.py
│   ├── test_tags.py
│   └── ...
├── services/         # Service layer tests
│   └── test_rfid_*.py
├── conftest.py       # Test fixtures
└── test_*.py         # Unit tests
```

## RFID Integration

The backend supports RFID tag tracking via the Chafon CF-H906 reader.

### Configuration

Set these environment variables in `.env`:

```env
RFID_READER_IP=192.168.1.100
RFID_READER_PORT=4001
RFID_CONNECTION_TYPE=wifi    # wifi, bluetooth, or serial
RFID_SIMULATION_MODE=True    # Set False for real hardware
```

### WebSocket Real-time Updates

Connect to `/ws/rfid` for real-time tag scan notifications:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/rfid');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Tag scanned:', data);
};
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/tags/` | GET | List all tags |
| `/api/v1/tags/{epc}` | GET | Get tag by EPC |
| `/api/v1/tags/` | POST | Create/update tag |
| `/api/v1/tags/stats` | GET | Tag statistics |
