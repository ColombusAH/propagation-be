# Shifty

Shifty is a comprehensive shift management application.

## Project Structure

- `be/` - Backend service (FastAPI + Prisma + PostgreSQL)
- `fe/` - Frontend service (coming soon)

## Railway Deployment

This project is configured for deployment on Railway. The main configuration files are:

- `railway.toml` - Railway configuration
- `Dockerfile` - Docker build for Railway deployment

### How to Deploy

1. **Create a Railway Project**:
   - Go to [Railway Dashboard](https://railway.app)
   - Create a new project
   - Add a PostgreSQL database service

2. **Deploy the Backend**:
   - Connect your GitHub repository
   - Railway will automatically:
     - Build using the Dockerfile
     - Configure environment variables
     - Apply database migrations

3. **Set Required Environment Variables**:
   - `SECRET_KEY` - Must be set manually in Railway Dashboard

### Local Development

For local development, see the README files in the respective directories:

- Backend: [be/README.md](be/README.md)

## License

This project is proprietary and confidential. 