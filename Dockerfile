# Build stage
FROM node:20-slim AS build

WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./
RUN npm install

# Copy source and build
COPY . .
RUN npm run build

# Production stage
FROM node:20-slim

WORKDIR /app

# Copy the build output and production dependencies
COPY --from=build /app/build ./build
COPY --from=build /app/package.json ./package.json
COPY --from=build /app/node_modules ./node_modules

# Expose the frontend port
EXPOSE 3000

# Run the standalone Node server
CMD ["node", "build"]
