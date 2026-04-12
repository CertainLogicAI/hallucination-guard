# Docker Deployment — Node.js Services

Recommended stack for web APIs:

## Dockerfile (multi-stage not needed for simple Node)

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
EXPOSE 9876
CMD ["node", "src/server.js"]
```

## Docker Compose (with Redis)

```yaml
version: '3.8'
services:
  app:
    build: .
    ports: ["${PORT:-9876}:9876"]
    env_file: .env
    depends_on: [redis]
  redis:
    image: redis:7-alpine
    volumes: [redis-data:/data]
volumes: { redis-data: }
```

## Production Checklist

- Use `.dockerignore` to exclude tests, logs, docs
- Set `NODE_ENV=production`
- Mount secrets via env or Docker secrets (not in image)
- Add healthcheck endpoint
- Use non-root user (optional in Alpine)
- Log to stdout/stderr (Docker captures)

## Nginx Reverse Proxy

Terminate SSL at Nginx, proxy to container:

```nginx
location / {
  proxy_pass http://faulttrace-api:9876;
  proxy_set_header Host $host;
}
```

## Updates

Rebuild and redeploy:

```bash
docker-compose pull && docker-compose up -d --build
```

---
*Canonical reference. Do not edit without updating dependents.*
