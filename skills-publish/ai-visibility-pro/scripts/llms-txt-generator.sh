#!/usr/bin/env bash
# llms.txt Generator — Create AI-readable site descriptions
# Usage: ./llms-txt-generator.sh <url> [output-dir]
# Generates both llms.txt (summary) and llms-full.txt (detailed)

set -uo pipefail

URL="${1:-}"
OUTPUT_DIR="${2:-.}"

if [ -z "$URL" ]; then
  echo "Usage: $0 <url> [output-dir]"
  echo "Example: $0 https://example.com ./site"
  exit 1
fi

mkdir -p "$OUTPUT_DIR"

echo "🔍 Analyzing $URL for llms.txt generation..."

node -e "
const https = require('https');
const http = require('http');
const fs = require('fs');

const url = '$URL';
const outputDir = '$OUTPUT_DIR';
const domain = new URL(url).hostname;

function fetch(fetchUrl) {
  return new Promise((resolve, reject) => {
    const mod = fetchUrl.startsWith('https') ? https : http;
    const req = mod.get(fetchUrl, { headers: { 'User-Agent': 'Mozilla/5.0 (compatible; LLMSGenerator/1.0)' }, timeout: 10000 }, (res) => {
      if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
        const loc = res.headers.location.startsWith('http') ? res.headers.location : new URL(res.headers.location, fetchUrl).href;
        return fetch(loc).then(resolve).catch(reject);
      }
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => resolve({ status: res.statusCode, body: data }));
    });
    req.on('error', e => resolve({ status: 0, body: '', error: e.message }));
    req.on('timeout', () => { req.destroy(); resolve({ status: 0, body: '' }); });
  });
}

function extractText(html) {
  return html
    .replace(/<script[^>]*>[\s\S]*?<\/script>/gi, '')
    .replace(/<style[^>]*>[\s\S]*?<\/style>/gi, '')
    .replace(/<[^>]+>/g, ' ')
    .replace(/\\s+/g, ' ')
    .trim();
}

function extractTitle(html) {
  const m = html.match(/<title[^>]*>([^<]+)<\/title>/i);
  return m ? m[1].trim() : domain;
}

function extractDescription(html) {
  const m = html.match(/meta[^>]*name=[\"']description[\"'][^>]*content=[\"']([^\"']*)[\"']/i);
  return m ? m[1].trim() : '';
}

function extractHeadings(html) {
  const headings = [];
  const regex = /<h[12][^>]*>(.*?)<\/h[12]>/gi;
  let match;
  while ((match = regex.exec(html)) !== null) {
    const text = match[1].replace(/<[^>]+>/g, '').trim();
    if (text) headings.push(text);
  }
  return headings;
}

function extractLinks(html, baseUrl) {
  const links = new Set();
  const regex = /href=[\"']([^\"']+)[\"']/gi;
  let match;
  while ((match = regex.exec(html)) !== null) {
    const href = match[1];
    if (href.startsWith('/') && !href.startsWith('//')) {
      links.add(new URL(href, baseUrl).href);
    } else if (href.startsWith(baseUrl)) {
      links.add(href);
    }
  }
  return [...links].filter(l => !l.match(/\.(css|js|png|jpg|svg|gif|ico|woff|tar|gz)$/i));
}

async function generate() {
  const page = await fetch(url);
  if (page.status !== 200) {
    console.error('Failed to fetch:', url, 'Status:', page.status);
    process.exit(1);
  }
  
  const title = extractTitle(page.body);
  const description = extractDescription(page.body);
  const headings = extractHeadings(page.body);
  const text = extractText(page.body);
  const internalLinks = extractLinks(page.body, url);
  
  // Fetch sub-pages for more context (max 5)
  const subPages = [];
  for (const link of internalLinks.slice(0, 5)) {
    const sub = await fetch(link);
    if (sub.status === 200) {
      subPages.push({
        url: link,
        title: extractTitle(sub.body),
        description: extractDescription(sub.body),
        headings: extractHeadings(sub.body),
        textPreview: extractText(sub.body).substring(0, 500)
      });
    }
  }
  
  // Generate llms.txt (summary)
  let llmsTxt = '# ' + title + '\\n\\n';
  if (description) llmsTxt += '> ' + description + '\\n\\n';
  
  llmsTxt += '## What This Site Does\\n';
  llmsTxt += 'Based on page analysis: ';
  if (headings.length > 0) {
    llmsTxt += headings.slice(0, 5).join(', ') + '\\n\\n';
  } else {
    llmsTxt += text.substring(0, 200) + '\\n\\n';
  }
  
  if (subPages.length > 0) {
    llmsTxt += '## Pages\\n';
    subPages.forEach(sp => {
      llmsTxt += '- [' + sp.title + '](' + sp.url + ')';
      if (sp.description) llmsTxt += ' — ' + sp.description;
      llmsTxt += '\\n';
    });
    llmsTxt += '\\n';
  }
  
  llmsTxt += '## Links\\n';
  llmsTxt += '- Website: ' + url + '\\n';
  llmsTxt += '- Detailed info: ' + url.replace(/\\/?$/, '/llms-full.txt') + '\\n';
  
  // Generate llms-full.txt (detailed)
  let llmsFull = '# ' + title + ' — Complete Reference\\n\\n';
  llmsFull += '## About\\n';
  if (description) llmsFull += description + '\\n\\n';
  llmsFull += '## Main Page Content\\n';
  llmsFull += text.substring(0, 2000) + '\\n\\n';
  
  if (subPages.length > 0) {
    llmsFull += '## Site Pages\\n\\n';
    subPages.forEach(sp => {
      llmsFull += '### ' + sp.title + '\\n';
      llmsFull += '**URL:** ' + sp.url + '\\n';
      if (sp.description) llmsFull += sp.description + '\\n';
      if (sp.headings.length > 0) llmsFull += '**Sections:** ' + sp.headings.join(', ') + '\\n';
      llmsFull += sp.textPreview + '...\\n\\n';
    });
  }
  
  llmsFull += '## Contact\\n';
  llmsFull += '- Website: ' + url + '\\n';
  
  // Write files
  fs.writeFileSync(outputDir + '/llms.txt', llmsTxt);
  fs.writeFileSync(outputDir + '/llms-full.txt', llmsFull);
  
  console.log('Generated ' + llmsTxt.length + ' byte llms.txt');
  console.log('Generated ' + llmsFull.length + ' byte llms-full.txt');
}

generate().catch(e => console.error('Error:', e.message));
" 2>&1

echo "✅ Files saved to $OUTPUT_DIR/llms.txt and $OUTPUT_DIR/llms-full.txt"
