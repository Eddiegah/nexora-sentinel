# frontend/Dockerfile
# Tells Docker how to build and run the React dashboard

# Stage 1 — Build the React app
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files first
COPY frontend/package*.json ./

# Install dependencies
RUN npm install

# Copy all frontend source code
COPY frontend/ .

# Build the production version of React
RUN npm run build

# Stage 2 — Serve with nginx
FROM nginx:alpine

# Copy the built React app to nginx
COPY --from=builder /app/build /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# nginx starts automatically
CMD ["nginx", "-g", "daemon off;"]