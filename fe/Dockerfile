FROM node:22.3.0-alpine as build

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci

# Copy source files
COPY . .

# Build the app
RUN npm run build

FROM nginx:1.25-alpine

# Copy built files from build stage
COPY --from=build /app/dist /usr/share/nginx/html
# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Create entrypoint script for dynamic port configuration
RUN echo '#!/bin/sh' > /docker-entrypoint.sh && \
    echo 'if [ -n "$PORT" ]; then' >> /docker-entrypoint.sh && \
    echo '  sed -i "s/listen 80/listen $PORT/g" /etc/nginx/conf.d/default.conf' >> /docker-entrypoint.sh && \
    echo 'fi' >> /docker-entrypoint.sh && \
    echo 'echo "Nginx configuration:"' >> /docker-entrypoint.sh && \
    echo 'cat /etc/nginx/conf.d/default.conf' >> /docker-entrypoint.sh && \
    echo 'exec nginx -g "daemon off;"' >> /docker-entrypoint.sh && \
    chmod +x /docker-entrypoint.sh

# Expose the port (Railway will override this with their PORT env var)
EXPOSE 80

# Start the server
ENTRYPOINT ["/docker-entrypoint.sh"] 