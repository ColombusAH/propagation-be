FROM node:22.3.0-alpine as build

WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm ci

# Copy source files
COPY . .

# Build the app
RUN npm run build

RUN ls -la

FROM nginx:1.25-alpine

# Copy built files from build stage
COPY --from=build /app/dist /usr/share/nginx/html
COPY --from=build /app/nginx.conf /etc/nginx/conf.d/default.conf

# Expose the port (Railway will override this with their PORT env var)
EXPOSE 80

# Run dynamic port substitution and start Nginx in the foreground
CMD if [ -n "$PORT" ]; then \
      sed -i "s/listen 80;/listen $PORT;/g" /etc/nginx/conf.d/default.conf; \
    fi && \
    echo "Nginx configuration:" && \
    cat /etc/nginx/conf.d/default.conf && \
    nginx -g "daemon off;"