FROM node:18-bullseye-slim
WORKDIR /app

# Copy lockfile, install dependencies
COPY package.json package-lock.json ./
RUN npm install \
  && npm install @rollup/rollup-linux-x64-gnu --save-optional

# Copy the rest of your app
COPY . .
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]