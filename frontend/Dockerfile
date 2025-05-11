FROM node:18-alpine

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json ./
RUN npm ci

# Copy source
COPY . ./

# Expose Vite dev server port
EXPOSE 5173

# Launch Vite in host mode for container
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]