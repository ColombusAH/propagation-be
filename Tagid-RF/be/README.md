# Shifty Backend

[![Backend CI](https://github.com/ColombusAH/propagation-be/actions/workflows/backend-ci.yml/badge.svg)](https://github.com/ColombusAH/propagation-be/actions/workflows/backend-ci.yml)
[![Frontend CI](https://github.com/ColombusAH/propagation-be/actions/workflows/frontend-ci.yml/badge.svg)](https://github.com/ColombusAH/propagation-be/actions/workflows/frontend-ci.yml)

Backend service for Shifty application.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Generate Prisma client
prisma generate

# Run the application
uvicorn app.main:app --reload
```

## Testing

```bash
# Run all unit tests
pytest tests/unit -v

# Run with coverage report
pytest tests/unit -v --cov=app --cov-report=html

# Check code quality
flake8 app/ --count --statistics
black --check app/ tests/
isort --check-only app/ tests/
```

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

debug:
python -m debugpy --listen 0.0.0.0:5679 --wait-for-client \
  -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

python -m debugpy --listen 0.0.0.0:5679 --wait-for-client -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload


connect reader:
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/tags/reader/connect" -Method POST -ContentType "application/json"


PG admin user:
username: admin@admin.com
password: admin
