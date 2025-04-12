FROM node:22.3.0-alpine as build

WORKDIR /app
# First copy only package files to leverage caching
COPY package*.json ./
RUN npm ci --quiet

# Then copy the rest and build
COPY . .
RUN npm run build

# Use slim version for smaller image
FROM nginx:1.25-alpine

# Create a simple health check file
RUN mkdir -p /usr/share/nginx/html/healthz && \
    echo "ok" > /usr/share/nginx/html/healthz/index.html && \
    chmod 644 /usr/share/nginx/html/healthz/index.html

# Install minimal requirements
RUN apk add --no-cache bash

# Copy build results and config
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

# Copy entrypoint script
COPY entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Set environment variables
ENV PORT=80
ENV ENABLE_ALPINE_PRIVATE_NETWORKING=true

EXPOSE 80

# Use healthcheck instruction
HEALTHCHECK --interval=5s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -q -O - http://localhost:$PORT/healthz || exit 1

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]