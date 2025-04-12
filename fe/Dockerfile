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

# Install minimal requirements - add iproute2 for ip command and curl for healthcheck
RUN apk add --no-cache bash iproute2 curl

# Copy build results and config
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

# Copy entrypoint script
COPY entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Set environment variables
ENV PORT=80
# Railway handles networking, so we're disabling our custom implementation
ENV ENABLE_ALPINE_PRIVATE_NETWORKING=true

EXPOSE 80

# Use healthcheck instruction with more generous settings
HEALTHCHECK --interval=10s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:80/healthz || exit 1

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]