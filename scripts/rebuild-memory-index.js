#!/usr/bin/env node
/**
 * rebuild-memory-index.js — Cron wrapper around memory-index.js
 *
 * Builds the reverse tag index for memory/*.md files.
 * Kept as a separate file so the cron job path is stable.
 */

const { buildIndex } = require('./memory-index.js');

buildIndex();
