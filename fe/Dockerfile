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

# Create a proper entrypoint script without escape issues
RUN echo '#!/bin/sh' > /docker-entrypoint.sh && \
    echo 'sed -i "s/listen 80/listen ${PORT:-80}/g" /etc/nginx/conf.d/default.conf' >> /docker-entrypoint.sh && \
    echo 'nginx -g "daemon off;"' >> /docker-entrypoint.sh && \
    chmod +x /docker-entrypoint.sh

# Expose the port
EXPOSE 80

# Start the server
CMD ["/docker-entrypoint.sh"] 