/**
 * CertainLogic Source-Type Boost Map
 *
 * Extension to DEFAULT_SOURCE_BOOSTS that maps CertainLogic-specific
 * slug prefixes to boost multipliers.
 *
 * These boosts encode the Moat Thesis: curated strategy/concepts rank
 * highest, product pages rank highly (data flywheel), evidence/metrics
 * rank above noisy bulk content.
 *
 * Merged into DEFAULT_SOURCE_BOOSTS at engine init time.
 * Override via env: GBRAIN_SOURCE_BOOST (prefix syntax same as default).
 */

export const CERTAINLOGIC_SOURCE_BOOSTS: Record<string, number> = {
  // Moat thesis and strategic principles — curated, opinionated
  'concepts/certainlogic-': 1.8,
  'concepts/deterministic-ai': 1.7,
  'concepts/open-source-strategy': 1.6,

  // Product pages — data flywheel, hard to replicate
  'projects/faulttrace': 1.6,
  'projects/brain-api': 1.6,
  'projects/agentpathfinder': 1.5,
  'projects/': 1.3, // general project pages

  // Strategy nodes — high-signal operational context
  'family/work/strategy/': 1.5,
  'family/work/evidence/': 1.4,

  // Metrics and reports — data-rich, objective
  'family/work/metrics/': 1.3,
  'family/work/reports/': 1.3,
  'family/work/templates/': 1.2,

  // Infrastructure and operations — utility content
  'family/work/infrastructure/': 1.1,

  // Comms and content — moderate signal
  'family/comms/': 1.1,

  // Neutral: YC context, civic — not our moat but relevant
  'yc/': 1.0,
  'civic/': 1.0,

  // Demoted: family/personal nodes that aren't work-related
  'family/personal/': 0.6,
  'family/home/': 0.6,
};

/**
 * Merge CertainLogic boosts with the default boost map.
 * CertainLogic-specific prefixes override defaults (longest-prefix-match
 * in sql-ranking.ts handles conflicts correctly).
 */
export function mergeCertainLogicBoosts(
  defaults: Record<string, number>,
): Record<string, number> {
  return { ...defaults, ...CERTAINLOGIC_SOURCE_BOOSTS };
}
