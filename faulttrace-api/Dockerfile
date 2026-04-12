FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .

# Default port (overridable via FAULTRACE_PORT env)
EXPOSE 9876

# Use entrypoint to wait for Redis
ENTRYPOINT ["node", "docker-entrypoint.js"]
CMD []