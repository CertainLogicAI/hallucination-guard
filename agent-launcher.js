#!/usr/bin/env node
/**
 * OpenClaw Agent Launcher with Workspace Cache Preload
 *
 * Usage: Instead of running agents directly, use this launcher.
 *
 * Example:
 *   node agent-launcher.js <agentId> <task>
 *
 * This sets NODE_OPTIONS to preload the workspace cache, giving all agents
 * instant access to getRelevantFiles(), getFileSummary(), getReference().
 */

const { spawn } = require('child_process');
const path = require('path');

const ROOT = '/data/.openclaw/workspace';
const CACHE_CLIENT = path.join(ROOT, 'workspace-cache-client.js');

// Ensure cache exists
if (!require('fs').existsSync(CACHE_CLIENT)) {
  console.error('Workspace cache client not found. Run build first.');
  process.exit(1);
}

// Forward all arguments to the actual agent command
const [agentId, ...taskParts] = process.argv.slice(2);
if (!agentId) {
  console.error('Usage: node agent-launcher.js <agentId> <task...>');
  process.exit(1);
}

const task = taskParts.join(' ');

// Build command: openclaw agent run (or sessions_spawn via CLI)
// We'll use the openclaw CLI if available
const cmd = 'openclaw';
const args = ['agent', 'run', '--agent', agentId, '--task', task];

const env = {
  ...process.env,
  NODE_OPTIONS: `--require ${CACHE_CLIENT}`
};

const child = spawn(cmd, args, {
  env,
  stdio: 'inherit',
  detached: false
});

child.on('close', (code) => {
  process.exit(code);
});

child.on('error', (err) => {
  console.error('Failed to launch agent:', err.message);
  process.exit(1);
});
