# Build stage for Node.js and Prisma
FROM node:20-slim AS prisma-builder

WORKDIR /app

# Install Prisma CLI
RUN npm install -g prisma@latest

# Copy only the necessary files for Prisma
COPY prisma ./prisma

# Generate Prisma client
RUN prisma generate

# Final stage
FROM python:3.12-slim

WORKDIR /code

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Copy Prisma client from builder stage
COPY --from=prisma-builder /app/node_modules/.prisma /code/node_modules/.prisma

# Set environment variables
ENV DATABASE_URL=postgresql://postgres:postgres@db:5432/shifty
ENV PRISMA_ENGINES_CHECKSUM_IGNORE_MISSING=1

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--reload"]