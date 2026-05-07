/**
 * CertainLogic Intent Patterns
 *
 * Extension to the base intent classifier in intent.ts.
 * Detects queries that map to CertainLogic's strategic concerns:
 * moat, product, data/evidence, and operations.
 *
 * These patterns are CHECKED AFTER the base patterns in classifyQueryIntent
 * so that temporal/event/entity queries still win when they overlap.
 */

// Strategy / moat queries
export const STRATEGY_PATTERNS = [
  /\bmoat\b/i,
  /\bstrategy\b/i,
  /\bstrategic\b/i,
  /\bcompetitive advantage\b/i,
  /\bdefensib(le|ility)\b/i,
  /\bwhy\s+(certainlogic|us|we)\b/i,
  /\bwhat('s| is|s)\s+our\s+(moat|edge|advantage)\b/i,
  /\bhow\s+(do|does|can|will)\s+we\s+compete\b/i,
  /\bdata\s+flywheel\b/i,
  /\boutcome-aligned\b/i,
  /\btrade secret\b/i,
  /\bpatent\b/i,
  /\bip\s+(strategy|attorney|review)\b/i,
  /\bmonth[- ]?6\b/i, // "month 6" IP decision
];

// Product / feature queries
export const PRODUCT_PATTERNS = [
  /\bfaulttrace\b/i,
  /\bbrain\s+api\b/i,
  /\bdeterministic\s+ai\b/i,
  /\bagentpathfinder\b/i,
  /\bhybrid\s+router\b/i,
  /\b(token|context)\s+reduction\b/i,
  /\b(what|how)\s+does\s+(it|faulttrace|brain|agentpathfinder)\s+(work|do)\b/i,
  /\bL5X\b/i,
  /\bplc\b/i,
  /\bschematic\b/i,
  /\bparser\b/i,
  /\bwriter\b/i,
];

// Evidence / metrics / benchmark queries
export const DATA_PATTERNS = [
  /\bbenchmark\b/i,
  /\bmetrics?\b/i,
  /\bperformance\b/i,
  /\bevidence\b/i,
  /\bproof\b/i,
  /\b(test|tested|testing|tests)\b/i,
  /\baccuracy\b/i,
  /\bcache\s+hit\b/i,
  /\btoken\s+sav(ings|ed)\b/i,
  /\bhallucination\b/i,
  /\balignment\s+score\b/i,
  /\bhow\s+(many|much|well|accurate)\b/i,
  /\bresults?\b/i,
];

// Operations / business queries
export const OPERATIONS_PATTERNS = [
  /\bfunding\b/i,
  /\bpricing\b/i,
  /\bpartner(ship)?\b/i,
  /\bYC\b/,
  /\bhackathon\b/i,
  /\bteam\b/i,
  /\bhiring\b/i,
  /\brevenue\b/i,
  /\bcost\b/i,
  /\bmonthly\b/i,
  /\broadmap\b/i,
  /\bpriorit(y|ize)\b/i,
];

/**
 * Map CertainLogic intent to detail level.
 *
 * strategy   → 'high'   (need timeline + full context for decisions)
 * product    → 'high'   (need technical depth)
 * data       → 'high'   (need metrics, evidence)
 * operations → 'medium' (compiled truth sufficient)
 */
export function certainLogicIntentToDetail(intent: string): 'low' | 'medium' | 'high' | undefined {
  switch (intent) {
    case 'strategy': return 'high';
    case 'product': return 'high';
    case 'data': return 'high';
    case 'operations': return 'medium';
    default: return undefined;
  }
}

/**
 * Classify a CertainLogic-specific intent from query text.
 * Returns the intent string or null if no match.
 */
export function classifyCertainLogicIntent(query: string): string | null {
  if (STRATEGY_PATTERNS.some(p => p.test(query))) return 'strategy';
  if (PRODUCT_PATTERNS.some(p => p.test(query))) return 'product';
  if (DATA_PATTERNS.some(p => p.test(query))) return 'data';
  if (OPERATIONS_PATTERNS.some(p => p.test(query))) return 'operations';
  return null;
}
