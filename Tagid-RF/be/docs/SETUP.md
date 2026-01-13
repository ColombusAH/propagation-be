# Setup Guide for New Repository

This guide will help you set up the RFID Tracking MVP backend in a new Git repository.

## Step 1: Initialize Git Repository

```bash
cd be
git init
git add .
git commit -m "Initial commit: RFID Tracking MVP Backend"
```

## Step 2: Create Remote Repository

1. Create a new repository on GitHub/GitLab/Bitbucket
2. Copy the repository URL

## Step 3: Connect to Remote

```bash
git remote add origin <your-repo-url>
git branch -M main
git push -u origin main
```

## Step 4: Environment Setup

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your actual values:
   - `DATABASE_URL`: Your PostgreSQL connection string
   - `SECRET_KEY`: Generate a secure secret key
   - `RFID_READER_IP`: Your CF-H906 reader IP (if you have one)
   - Other settings as needed

3. **Important**: `.env` is already in `.gitignore` - never commit it!

## Step 5: Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Step 6: Database Setup

1. Make sure PostgreSQL is running
2. Create a database:
   ```sql
   CREATE DATABASE rfid_mvp;
   ```

3. Update `.env` with your database URL:
   ```
   DATABASE_URL=postgresql://user:password@localhost:5432/rfid_mvp
   ```

4. The application will automatically create tables on first run

## Step 7: Run the Application

```bash
uvicorn app.main:app --reload
```

The API will be available at:
- http://localhost:8000
- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/redoc (ReDoc)

## Step 8: Verify Installation

1. Check health endpoint:
   ```bash
   curl http://localhost:8000/health
   ```

2. Test API documentation:
   - Open http://localhost:8000/docs in your browser
   - Try the `/api/v1/tags/stats/summary` endpoint

3. Test WebSocket connection:
   - Use a WebSocket client or browser console:
   ```javascript
   const ws = new WebSocket('ws://localhost:8000/ws/rfid');
   ws.onmessage = (e) => console.log(JSON.parse(e.data));
   ```

## Files to Review Before Pushing

Make sure these files are properly configured:

- ✅ `.gitignore` - Excludes sensitive files (.env, __pycache__, etc.)
- ✅ `.env.example` - Template for environment variables
- ✅ `requirements.txt` - All dependencies listed
- ✅ `README.md` or `RFID_README.md` - Documentation
- ✅ `app/main.py` - Main application entry point

## Common Issues

### Database Connection Error
- Verify PostgreSQL is running
- Check `DATABASE_URL` in `.env`
- Ensure database exists

### Import Errors
- Make sure you're in the virtual environment
- Run `pip install -r requirements.txt` again
- Check Python version (3.9+)

### Port Already in Use
- Change port: `uvicorn app.main:app --reload --port 8001`
- Or stop the process using port 8000

## Next Steps

1. Review the [RFID_README.md](./RFID_README.md) for complete documentation
2. Configure RFID reader connection (if you have hardware)
3. Set up frontend integration
4. Deploy to production (Railway, Heroku, etc.)

## Deployment

For production deployment:

1. Set `DEBUG=False` in environment
2. Configure proper CORS origins
3. Use HTTPS/WSS
4. Set up proper logging
5. Configure database connection pooling
6. Add authentication/authorization

See deployment documentation for your platform of choice.

