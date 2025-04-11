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

# Railway will assign a PORT environment variable
# We need to replace the default NGINX port with the Railway PORT at runtime
# Create a script to handle this
RUN echo '#!/bin/sh \n\
sed -i "s/listen 80/listen \${PORT:-80}/g" /etc/nginx/conf.d/default.conf \n\
nginx -g "daemon off;"' > /docker-entrypoint.sh && \
chmod +x /docker-entrypoint.sh

# Expose the port
EXPOSE 80

# Start the server
CMD ["/docker-entrypoint.sh"] 