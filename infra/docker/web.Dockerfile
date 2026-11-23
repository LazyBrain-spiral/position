# Multi-stage production Dockerfile for Web Frontend
FROM node:24-alpine AS builder

WORKDIR /workspace

COPY package.json package-lock.json* ./
COPY apps/web/package.json ./apps/web/

RUN npm ci

COPY apps/web/ ./apps/web/

WORKDIR /workspace/apps/web
RUN npm run build

# Lightweight NGINX serving stage
FROM nginx:alpine AS runner

COPY --from=builder /workspace/apps/web/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
