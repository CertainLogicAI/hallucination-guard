/**
 * Analyzer Types — Strict schema for FaultTrace API output
 * This is the contract between the analyzer and the API.
 */

/**
 * @typedef {Object} AnalysisMetadata
 * @property {string} fileName - Original filename
 * @property {number} fileSize - Bytes
 * @property {string} analyzerVersion - Semantic version
 * @property {string} analyzedAt - ISO timestamp
 * @property {string|null} requestId - Optional tracking ID
 * @property {string|null} ip - Client IP (for logging)
 */

/**
 * @typedef {Object} AnalysisSummary
 * @property {number} totalRungs
 * @property {number} totalTags
 * @property {number} warnings
 * @property {number} errors
 * @property {number} info
 */

/**
 * @typedef {Object} IssueLocation
 * @property {number} rung - Rung number (1-indexed)
 * @property {number} instructionIndex - Position within rung (optional)
 */

/**
 * @typedef {Object} AnalysisIssue
 * @property {string} id - Unique issue ID (rule + instance)
 * @property {'error'|'warning'|'info'} severity
 * @property {string} rule - Rule name (e.g., 'UnusedTag')
 * @property {string} message - Human-readable description
 * @property {IssueLocation} location
 * @property {string} [suggestion] - Optional fix suggestion
 */

/**
 * @typedef {Object} TagInfo
 * @property {string} name
 * @property {string} type - BOOL, DINT, REAL, etc.
 * @property {boolean} used
 */

/**
 * @typedef {Object} IOMap
 * @property {Array<{name: string, type: string, address: string}>} inputs
 * @property {Array<{name: string, type: string, address: string}>} outputs
 */

/**
 * @typedef {Object} AnalysisReport
 * @property {AnalysisMetadata} metadata
 * @property {AnalysisSummary} summary
 * @property {AnalysisIssue[]} issues
 * @property {IOMap} ioMap
 * @property {TagInfo[]} tags
 */

module.exports = {
  AnalysisReport: 'AnalysisReport' // TypeScript would use interface; JS uses runtime check
};
