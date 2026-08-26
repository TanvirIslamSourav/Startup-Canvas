# Multi-stage build for the React/Vite frontend served by nginx.
# Build context for this image is the repo root, e.g.:
#   docker build -f docker/frontend.Dockerfile -t sc_frontend .
FROM node:26-alpine AS builder

WORKDIR /app

# Copy manifests first so npm install is cached when only source changes.
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install --no-audit --no-fund

# Copy the rest of the frontend source.
COPY frontend/ ./

# Build the production bundle into /app/dist.
RUN npm run build

# ---- Runtime stage -------------------------------------------------------
FROM nginx:1.27-alpine

# Remove the default nginx static site.
RUN rm -rf /usr/share/nginx/html/*

# Copy the Vite output into nginx's html root.
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy the SPA-friendly nginx config from the docker/ folder, which lives
# inside this build context (repo root).
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -qO- http://127.0.0.1/ >/dev/null || exit 1

CMD ["nginx", "-g", "daemon off;"]
