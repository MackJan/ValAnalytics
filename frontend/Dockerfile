# Build stage
FROM node:20-bullseye-slim AS builder
WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install all dependencies (including devDependencies for building)
RUN npm ci

# Copy source code and config files
COPY . .

# Set build-time environment variables for Vite
ARG VITE_API_URL=/api
ARG VITE_WS_URL=wss://152.53.65.38

ENV VITE_API_URL=$VITE_API_URL
ENV VITE_WS_URL=$VITE_WS_URL

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy our custom nginx config from the builder stage
COPY --from=builder /app/nginx.conf /etc/nginx/conf.d/default.conf

# Copy built application from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Create a non-root user for better security
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001

# Create a startup script to handle environment variables at runtime
RUN echo '#!/bin/sh' > /docker-entrypoint.d/30-envsubst-on-templates.sh && \
    echo 'set -e' >> /docker-entrypoint.d/30-envsubst-on-templates.sh && \
    echo 'echo "Starting nginx with custom config..."' >> /docker-entrypoint.d/30-envsubst-on-templates.sh && \
    chmod +x /docker-entrypoint.d/30-envsubst-on-templates.sh

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
