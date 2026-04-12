#!/usr/bin/env node
/**
 * Docker entrypoint script
 * Waits for Redis to be ready before starting the server.
 */

const { execSync } = require('child_process');
const Redis = require('ioredis');

const MAX_RETRIES = 30;
const RETRY_INTERVAL = 1000; // 1 second

function waitForRedis(redisUrl) {
  const client = new Redis(redisUrl);
  let attempts = 0;

  return new Promise((resolve, reject) => {
    function tryConnect() {
      attempts++;
      client.ping()
        .then(() => {
          console.log('Redis is ready');
          client.quit();
          resolve();
        })
        .catch(err => {
          if (attempts >= MAX_RETRIES) {
            client.quit();
            reject(new Error(`Redis not ready after ${MAX_RETRIES} attempts: ${err.message}`));
          } else {
            console.log(`Waiting for Redis (attempt ${attempts}/${MAX_RETRIES})...`);
            setTimeout(tryConnect, RETRY_INTERVAL);
          }
        });
    }
    tryConnect();
  });
}

async function main() {
  try {
    const redisUrl = process.env.REDIS_URL || 'redis://redis:6379';
    await waitForRedis(redisUrl);
    // Start the server
    require('./src/server');
  } catch (err) {
    console.error('Failed to start:', err.message);
    process.exit(1);
  }
}

main();
