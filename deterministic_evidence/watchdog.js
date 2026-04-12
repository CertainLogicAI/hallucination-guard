#!/usr/bin/env node
/**
 * Watchdog script to periodically rebuild the TF-IDF memory index.
 * Runs every 12 hours and logs activity to /data/.openclaw/logs/watchdog.log
 */

const { execFile } = require('child_process');
const path = require('path');
const fs = require('fs');

// Configuration
const INDEX_SCRIPT = path.join('/data/.openclaw', 'embedding-provider.js');
const LOG_FILE = path.join('/data/.openclaw', 'logs', 'watchdog.log');
const INTERVAL_MS = 12 * 60 * 60 * 1000; // 12 hours

/**
 * Logs a message with timestamp to the log file and console
 * @param {string} message - Message to log
 */
function logMessage(message) {
  const timestamp = new Date().toISOString();
  const logLine = `[${timestamp}] ${message}\n`;
  console.log(message.trim());
  fs.appendFileSync(LOG_FILE, logLine);
}

/**
 * Rebuilds the memory index by running embedding-provider.js index
 */
function rebuildIndex() {
  logMessage('Starting memory index rebuild...');
  
  // Check if the index script exists
  if (!fs.existsSync(INDEX_SCRIPT)) {
    logMessage(`ERROR: Index script not found at ${INDEX_SCRIPT}`);
    return;
  }
  
  // Run the index command
  execFile('node', [INDEX_SCRIPT, 'index'], (error, stdout, stderr) => {
    if (error) {
      logMessage(`ERROR: Index rebuild failed: ${error.message}`);
      if (stderr) logMessage(`STDERR: ${stderr}`);
      return;
    }
    
    if (stdout) logMessage(`Index rebuild output: ${stdout.trim()}`);
    logMessage('Memory index rebuild completed successfully');
  });
}

/**
 * Start the watchdog
 */
function startWatchdog() {
  logMessage('=== Memory Index Watchdog Started ===');
  logMessage(`Rebuild interval: ${INTERVAL_MS / (1000 * 60 * 60)} hours`);
  
  // Run immediately on startup
  rebuildIndex();
  
  // Schedule periodic rebuilds
  setInterval(rebuildIndex, INTERVAL_MS);
}

// Start the watchdog when this script is executed
startWatchdog();

// Handle graceful shutdown
process.on('SIGINT', () => {
  logMessage('Watchdog received SIGINT, shutting down...');
  process.exit(0);
});

process.on('SIGTERM', () => {
  logMessage('Watchdog received SIGTERM, shutting down...');
  process.exit(0);
});
