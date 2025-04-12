FROM node:22.3.0-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:1.25-alpine

# Install packages required for IPv6 private networking in Railway
RUN apk add --no-cache bash openssl curl

# Copy custom entrypoint script that will enable private networking
COPY entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Copy built files and nginx configuration
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

# Set environment variables
ENV PORT=80
ENV ENABLE_ALPINE_PRIVATE_NETWORKING=true

EXPOSE 80

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]