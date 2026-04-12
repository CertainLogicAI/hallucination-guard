#!/usr/bin/env bash
# GEO Audit — Check AI/LLM discoverability of any website
# Usage: ./geo-audit.sh <url> [output-file]
# Checks 12 signals across 4 categories, outputs scored report

set -uo pipefail

URL="${1:-}"
OUTPUT="${2:-workspace/artifacts/geo-audit-$(echo "$URL" | sed 's|https\?://||;s|/.*||').md}"

if [ -z "$URL" ]; then
  echo "Usage: $0 <url> [output-file]"
  echo "Example: $0 https://example.com"
  exit 1
fi

mkdir -p "$(dirname "$OUTPUT")"

echo "🔍 Running GEO audit on $URL ..."

node -e "
const https = require('https');
const http = require('http');

const url = '$URL';
const domain = new URL(url).hostname;

function fetch(fetchUrl) {
  return new Promise((resolve, reject) => {
    const mod = fetchUrl.startsWith('https') ? https : http;
    const req = mod.get(fetchUrl, { headers: { 'User-Agent': 'Mozilla/5.0 (compatible; GEOAudit/1.0)' }, timeout: 10000 }, (res) => {
      if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
        return fetch(res.headers.location).then(resolve).catch(reject);
      }
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => resolve({ status: res.statusCode, headers: res.headers, body: data }));
    });
    req.on('error', e => resolve({ status: 0, headers: {}, body: '', error: e.message }));
    req.on('timeout', () => { req.destroy(); resolve({ status: 0, headers: {}, body: '', error: 'timeout' }); });
  });
}

async function audit() {
  const results = [];
  let score = 0;
  let maxScore = 0;
  
  // Fetch main page
  const page = await fetch(url);
  const html = page.body.toLowerCase();
  
  // === CATEGORY 1: AI CRAWLER SIGNALS ===
  
  // 1. llms.txt
  maxScore += 3;
  const llmsTxt = await fetch(url.replace(/\\/?$/, '/llms.txt'));
  if (llmsTxt.status === 200 && llmsTxt.body.length > 50) {
    score += 3;
    results.push({ cat: 'AI Crawler Signals', check: 'llms.txt', status: '✅', score: '3/3', detail: 'Found (' + llmsTxt.body.length + ' bytes)' });
  } else {
    results.push({ cat: 'AI Crawler Signals', check: 'llms.txt', status: '❌', score: '0/3', detail: 'Missing — AI crawlers cant learn about your site' });
  }
  
  // 2. llms-full.txt
  maxScore += 2;
  const llmsFull = await fetch(url.replace(/\\/?$/, '/llms-full.txt'));
  if (llmsFull.status === 200 && llmsFull.body.length > 200) {
    score += 2;
    results.push({ cat: 'AI Crawler Signals', check: 'llms-full.txt', status: '✅', score: '2/2', detail: 'Found (' + llmsFull.body.length + ' bytes)' });
  } else {
    results.push({ cat: 'AI Crawler Signals', check: 'llms-full.txt', status: '❌', score: '0/2', detail: 'Missing — detailed reference for deep crawlers' });
  }
  
  // 3. robots.txt (allows AI bots)
  maxScore += 1;
  const robots = await fetch(url.replace(/\\/?$/, '/robots.txt'));
  if (robots.status === 200) {
    const blocksAI = /disallow.*\\/.*(?:gpt|anthropic|claude|perplexity|cohere)/i.test(robots.body);
    if (blocksAI) {
      results.push({ cat: 'AI Crawler Signals', check: 'robots.txt', status: '⚠️', score: '0/1', detail: 'Blocks AI crawlers — they cant index your content' });
    } else {
      score += 1;
      results.push({ cat: 'AI Crawler Signals', check: 'robots.txt', status: '✅', score: '1/1', detail: 'Present, allows AI crawlers' });
    }
  } else {
    score += 1;
    results.push({ cat: 'AI Crawler Signals', check: 'robots.txt', status: '✅', score: '1/1', detail: 'No robots.txt = everything allowed' });
  }
  
  // === CATEGORY 2: STRUCTURED DATA ===
  
  // 4. JSON-LD
  maxScore += 3;
  const jsonLdMatch = page.body.match(/application\\/ld\\+json/gi);
  if (jsonLdMatch) {
    score += 3;
    results.push({ cat: 'Structured Data', check: 'JSON-LD', status: '✅', score: '3/3', detail: jsonLdMatch.length + ' schema block(s) found' });
  } else {
    results.push({ cat: 'Structured Data', check: 'JSON-LD', status: '❌', score: '0/3', detail: 'No structured data — LLMs cant extract product/org info' });
  }
  
  // 5. Open Graph tags
  maxScore += 1;
  const ogTags = (page.body.match(/og:/gi) || []).length;
  if (ogTags >= 3) {
    score += 1;
    results.push({ cat: 'Structured Data', check: 'Open Graph', status: '✅', score: '1/1', detail: ogTags + ' OG tags found' });
  } else {
    results.push({ cat: 'Structured Data', check: 'Open Graph', status: '❌', score: '0/1', detail: 'Missing or incomplete OG tags' });
  }
  
  // 6. Semantic HTML (header, main, article, section, nav)
  maxScore += 1;
  const semanticTags = ['<header', '<main', '<article', '<section', '<nav'].filter(t => html.includes(t)).length;
  if (semanticTags >= 3) {
    score += 1;
    results.push({ cat: 'Structured Data', check: 'Semantic HTML', status: '✅', score: '1/1', detail: semanticTags + '/5 semantic tags used' });
  } else {
    results.push({ cat: 'Structured Data', check: 'Semantic HTML', status: '⚠️', score: '0/1', detail: semanticTags + '/5 semantic tags — LLMs parse semantic HTML better' });
  }
  
  // === CATEGORY 3: CITEABLE CONTENT ===
  
  // 7. FAQ section
  maxScore += 2;
  const hasFaq = html.includes('faq') || html.includes('frequently asked') || html.includes('questions');
  if (hasFaq) {
    score += 2;
    results.push({ cat: 'Citeable Content', check: 'FAQ Section', status: '✅', score: '2/2', detail: 'FAQ content detected — high citation potential' });
  } else {
    results.push({ cat: 'Citeable Content', check: 'FAQ Section', status: '❌', score: '0/2', detail: 'No FAQ found — FAQs are the #1 cited content type' });
  }
  
  // 8. Blog/articles
  maxScore += 2;
  const hasBlog = html.includes('/blog') || html.includes('article') || html.includes('posts');
  if (hasBlog) {
    score += 2;
    results.push({ cat: 'Citeable Content', check: 'Blog/Articles', status: '✅', score: '2/2', detail: 'Blog or article content detected' });
  } else {
    results.push({ cat: 'Citeable Content', check: 'Blog/Articles', status: '❌', score: '0/2', detail: 'No blog — LLMs cite articles, not sales pages' });
  }
  
  // 9. Heading depth (H1 > H2 > H3)
  maxScore += 1;
  const h1s = (page.body.match(/<h1/gi) || []).length;
  const h2s = (page.body.match(/<h2/gi) || []).length;
  const h3s = (page.body.match(/<h3/gi) || []).length;
  if (h1s >= 1 && h2s >= 2 && h3s >= 2) {
    score += 1;
    results.push({ cat: 'Citeable Content', check: 'Heading Hierarchy', status: '✅', score: '1/1', detail: h1s + ' H1, ' + h2s + ' H2, ' + h3s + ' H3 — good structure' });
  } else {
    results.push({ cat: 'Citeable Content', check: 'Heading Hierarchy', status: '⚠️', score: '0/1', detail: h1s + ' H1, ' + h2s + ' H2, ' + h3s + ' H3 — needs more depth' });
  }
  
  // === CATEGORY 4: DISCOVERABILITY ===
  
  // 10. Sitemap
  maxScore += 1;
  const sitemap = await fetch(url.replace(/\\/?$/, '/sitemap.xml'));
  if (sitemap.status === 200 && sitemap.body.includes('<urlset')) {
    score += 1;
    const urlCount = (sitemap.body.match(/<loc>/gi) || []).length;
    results.push({ cat: 'Discoverability', check: 'Sitemap', status: '✅', score: '1/1', detail: urlCount + ' URLs in sitemap' });
  } else {
    results.push({ cat: 'Discoverability', check: 'Sitemap', status: '❌', score: '0/1', detail: 'No sitemap — crawlers may miss pages' });
  }
  
  // 11. RSS feed
  maxScore += 1;
  const hasRss = html.includes('application/rss+xml') || html.includes('application/atom+xml');
  if (hasRss) {
    score += 1;
    results.push({ cat: 'Discoverability', check: 'RSS Feed', status: '✅', score: '1/1', detail: 'RSS/Atom feed linked' });
  } else {
    results.push({ cat: 'Discoverability', check: 'RSS Feed', status: '❌', score: '0/1', detail: 'No RSS feed — AI aggregators use RSS for content discovery' });
  }
  
  // 12. Meta description quality
  maxScore += 1;
  const descMatch = page.body.match(/meta[^>]*name=[\"']description[\"'][^>]*content=[\"']([^\"']*)[\"']/i);
  if (descMatch && descMatch[1].length >= 80 && descMatch[1].length <= 160) {
    score += 1;
    results.push({ cat: 'Discoverability', check: 'Meta Description', status: '✅', score: '1/1', detail: descMatch[1].length + ' chars — good length' });
  } else if (descMatch) {
    results.push({ cat: 'Discoverability', check: 'Meta Description', status: '⚠️', score: '0/1', detail: descMatch[1].length + ' chars — aim for 80-160' });
  } else {
    results.push({ cat: 'Discoverability', check: 'Meta Description', status: '❌', score: '0/1', detail: 'Missing — LLMs use this for page summaries' });
  }
  
  // Grade
  const pct = Math.round((score / maxScore) * 100);
  let grade = 'F';
  if (pct >= 90) grade = 'A';
  else if (pct >= 80) grade = 'A-';
  else if (pct >= 70) grade = 'B';
  else if (pct >= 60) grade = 'B-';
  else if (pct >= 50) grade = 'C';
  else if (pct >= 40) grade = 'D';
  
  // Output report
  let report = '# GEO Audit: ' + domain + '\\n';
  report += '**URL:** ' + url + '\\n';
  report += '**Scanned:** ' + new Date().toISOString().split('T')[0] + '\\n';
  report += '**Score:** ' + score + '/' + maxScore + ' (' + pct + '%) — Grade: ' + grade + '\\n\\n';
  report += '---\\n\\n';
  
  let currentCat = '';
  results.forEach(r => {
    if (r.cat !== currentCat) {
      currentCat = r.cat;
      report += '## ' + currentCat + '\\n\\n';
    }
    report += r.status + ' **' + r.check + '** (' + r.score + ')\\n';
    report += '  ' + r.detail + '\\n\\n';
  });
  
  report += '---\\n\\n';
  report += '## Priority Fixes\\n\\n';
  const failures = results.filter(r => r.status !== '✅');
  if (failures.length === 0) {
    report += 'All checks passed! Monitor monthly for changes.\\n';
  } else {
    failures.sort((a, b) => parseInt(b.score.split('/')[1]) - parseInt(a.score.split('/')[1]));
    failures.forEach((r, i) => {
      report += (i + 1) + '. **' + r.check + '** — ' + r.detail + '\\n';
    });
  }
  
  report += '\\n---\\nGenerated by AI Visibility Pro — GEO Audit\\n';
  
  require('fs').writeFileSync('$OUTPUT', report);
  
  console.log('Score: ' + score + '/' + maxScore + ' (' + pct + '%) — Grade: ' + grade);
  console.log('Report saved: $OUTPUT');
}

audit().catch(e => console.error('Error:', e.message));
" 2>&1

echo "✅ GEO audit saved: $OUTPUT"
