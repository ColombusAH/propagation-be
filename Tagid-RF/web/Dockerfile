# Stage 1: Build the application
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package management files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build args
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL

# Build the application
RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:alpine

# Remove default nginx static assets
RUN rm -rf /usr/share/nginx/html/*

# Copy built artifacts from builder stage (Vite builds to /dist by default)
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy custom nginx configuration template
# Cache bust to ensure latest nginx.conf is used
ARG CACHEBUST=10
COPY nginx.conf /etc/nginx/conf.d/default.conf.template

# Expose port (Railway will set PORT env variable)
EXPOSE 80

# Start Nginx with PORT, BACKEND_URL, and BACKEND_HOST substitution
CMD sh -c "BACKEND_HOST=$(echo $BACKEND_URL | awk -F/ '{print $3}') && export BACKEND_HOST && envsubst '\$PORT \$BACKEND_URL \$BACKEND_HOST' < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf && cat /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'"
