FROM node:22-alpine

# Set working directory
WORKDIR /data/.openclaw

# Copy necessary files
COPY embedding-provider.js .
COPY watchdog.js .
COPY config.json .
COPY manifest.json .
COPY scripts/ ./scripts/
COPY logs/ ./logs/
COPY backups/ ./backups/

# Create necessary directories and set permissions
RUN mkdir -p secrets && \
    chmod +x *.js && \
    chmod +x scripts/*.sh && \
    chown -R node:node /data/.openclaw

# Install dependencies if any
RUN npm install

# Expose port for HTTP search API
EXPOSE 8080

# Copy systemd unit file
COPY openclaw-watchdog.service /etc/systemd/system/

# Enable and start the service
RUN systemctl enable openclaw-watchdog.service

# Set entrypoint to start systemd and the service
CMD ["/bin/sh", "-c", "systemctl start openclaw-watchdog.service && systemctl status openclaw-watchdog.service && tail -f /var/log/syslog"]