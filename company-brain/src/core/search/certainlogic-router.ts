/**
 * CertainLogic Skills Router
 *
 * Maps queries to the right company brain layer and external tools
 * based on intent classification. Replaces hardcoded tool selection
 * with a deterministic, auditable routing table.
 *
 * Design priority: deterministic > accurate > comprehensive.
 */

import { classifyCertainLogicIntent } from './certainlogic-intent.ts';

// ── Types ────────────────────────────────────────────────────────────────

export type ToolAction = {
  tool: string;
  params: Record<string, unknown>;
};

export type RoutingResult = {
  primary: ToolAction;
  fallbacks: ToolAction[];
  intent: string;
  source_boost_hint: string; // slug prefix to boost in search
  explanation: string;
};

// ── Routing Table ────────────────────────────────────────────────────────

/**
 * Maps CertainLogic intent categories to actions.
 * Each entry defines what to do when the brain returns nothing useful.
 */
const ROUTING_TABLE: Record<string, {
  primary: string;
  fallbacks: string[];
  boost_prefix: string;
  explanation: string;
}> = {
  strategy: {
    primary: 'brain.query',
    fallbacks: ['brain.search', 'web.fetch'],
    boost_prefix: 'concepts/certainlogic-',
    explanation: 'Strategy queries → Brain concepts (moat thesis) with fallback to search',
  },
  product: {
    primary: 'brain.query',
    fallbacks: ['brain.search', 'web.fetch'],
    boost_prefix: 'projects/',
    explanation: 'Product queries → Brain project pages with fallback to web docs',
  },
  data: {
    primary: 'brain.query',
    fallbacks: ['brain.search', 'exec'],
    boost_prefix: 'family/work/metrics/',
    explanation: 'Data queries → Brain metrics/evidence pages; exec for live script runs',
  },
  operations: {
    primary: 'brain.query',
    fallbacks: ['brain.search', 'web.fetch'],
    boost_prefix: 'family/work/',
    explanation: 'Operations queries → Brain work pages with search fallback',
  },
};

// ── Public API ──────────────────────────────────────────────────────────

/**
 * Route a query through the CertainLogic routing table.
 *
 * @param query  — the user's query text
 * @returns      — routing result with primary action + fallbacks
 */
export function routeQuery(query: string): RoutingResult {
  const intent = classifyCertainLogicIntent(query) || 'general';

  if (intent === 'general') {
    return {
      primary: { tool: 'brain.search', params: { q: query, limit: 5 } },
      fallbacks: [
        { tool: 'web.fetch', params: { url: null } }, // placeholder — needs URL
      ],
      intent: 'general',
      source_boost_hint: 'family/work/',
      explanation: 'No CertainLogic-specific intent detected. Default to brain search.',
    };
  }

  const route = ROUTING_TABLE[intent];
  if (!route) {
    return {
      primary: { tool: 'brain.search', params: { q: query, limit: 5 } },
      fallbacks: [],
      intent,
      source_boost_hint: 'family/work/',
      explanation: `Intent '${intent}' has no route entry. Defaulting to search.`,
    };
  }

  return {
    primary: { tool: route.primary, params: { query } },
    fallbacks: route.fallbacks.map(t => ({ tool: t, params: { q: query } })),
    intent,
    source_boost_hint: route.boost_prefix,
    explanation: route.explanation,
  };
}

/**
 * Execute a routed query through the deterministic brain.
 *
 * This is the main entry point for skills → brain integration.
 * Returns the brain result with routing metadata.
 */
export async function executeRoutedQuery(
  query: string,
  brainQueryFn: (q: string) => Promise<unknown>,
): Promise<{ result: unknown; routing: RoutingResult }> {
  const routing = routeQuery(query);

  // Try primary action
  let result: unknown;
  try {
    result = await brainQueryFn(query);
  } catch (err) {
    // Primary failed — log and try fallbacks (simplified: just return error for now)
    result = {
      error: err instanceof Error ? err.message : String(err),
      _fallback_attempted: false, // TODO: implement fallback chain
    };
  }

  return { result, routing };
}

// ── Convenience: Build search options with source boost ──────────────────

/**
 * Build hybrid search options that apply the correct source boost
 * for a given query's intent.
 */
export function buildBoostedSearchOpts(query: string): {
  q: string;
  limit: number;
  detail?: 'low' | 'medium' | 'high';
  include_slug_prefixes?: string[];
} {
  const routing = routeQuery(query);
  return {
    q: query,
    limit: 5,
    detail: 'high',
    include_slug_prefixes: [routing.source_boost_hint],
  };
}
