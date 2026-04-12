// /data/.openclaw/embedding-provider.js
// Offline TF-IDF based embedding provider with HTTP API (no external deps)
const fs = require('fs');
const path = require('path');
const http = require('http');

// ---------- 1. Index Builder ----------
function buildIndex() {
  console.log('[INFO] Starting index build...');
  const memDir = '/data/.openclaw/workspace/memory';
  let files;
  try {
    files = fs.readdirSync(memDir).filter(f => f.endsWith('.md'));
  } catch (e) {
    console.error('[ERROR] Cannot read memory directory:', e.message);
    process.exit(1);
  }
  console.log('[INFO] Found', files.length, 'memory files');

  const docs = files.map(f => ({ id: f, text: fs.readFileSync(path.join(memDir, f), 'utf8') }));

  const termFreq = {};
  const docFreq = {};
  docs.forEach(doc => {
    const tokens = (doc.text.toLowerCase().match(/\b\w+\b/g) || []);
    const tf = {};
    tokens.forEach(t => { tf[t] = (tf[t] || 0) + 1; });
    termFreq[doc.id] = tf;
    Object.keys(tf).forEach(t => { docFreq[t] = (docFreq[t] || 0) + 1; });
  });

  const N = docs.length;
  const vectors = {};
  Object.entries(termFreq).forEach(([id, tf]) => {
    const vec = {};
    Object.entries(tf).forEach(([term, count]) => {
      const idf = Math.log(N / (docFreq[term] || 1));
      vec[term] = count * idf;
    });
    vectors[id] = vec;
  });

  const index = { vectors, docCount: N };
  fs.writeFileSync('/data/.openclaw/embeddings.json', JSON.stringify(index));
  console.log('[INFO] Index built –', N, 'documents');
}

// ---------- 2. Cosine Similarity ----------
function cosine(a, b) {
  let dot = 0, normA = 0, normB = 0;
  const terms = new Set([...Object.keys(a), ...Object.keys(b)]);
  terms.forEach(t => {
    const av = a[t] || 0;
    const bv = b[t] || 0;
    dot += av * bv;
    normA += av * av;
    normB += bv * bv;
  });
  return dot / (Math.sqrt(normA) * Math.sqrt(normB) + 1e-9);
}

// ---------- 3. Query ----------
function query(q, top = 5) {
  const data = JSON.parse(fs.readFileSync('/data/.openclaw/embeddings.json', 'utf8'));
  const tokens = (q.toLowerCase().match(/\b\w+\b/g) || []);
  const qVec = {};
  tokens.forEach(t => { qVec[t] = (qVec[t] || 0) + 1; });

  const scores = Object.entries(data.vectors).map(([id, vec]) => ({
    id,
    score: cosine(qVec, vec)
  }));
  scores.sort((a, b) => b.score - a.score);
  return scores.slice(0, top);
}

// ---------- 4. CLI handling ----------
const args = process.argv.slice(2);
if (args[0] === 'index') {
  buildIndex();
} else if (args[0] === 'search') {
  const q = args.slice(1).join(' ');
  console.log(JSON.stringify(query(q), null, 2));
} else if (args[0] === 'serve') {
  const port = parseInt(args[1], 10) || 8000;
  const server = http.createServer((req, res) => {
    if (req.url.startsWith('/search?')) {
      const q = decodeURIComponent(req.url.split('?')[1] || '');
      try {
        const result = query(q);
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(result));
      } catch (e) {
        res.writeHead(500, { 'Content-Type': 'text/plain' });
        res.end('Server error: ' + e.message);
      }
    } else {
      res.writeHead(404, { 'Content-Type': 'text/plain' });
      res.end('Not found');
    }
  });
  server.listen(port, () => console.log(`[INFO] Server listening on port ${port}`));
} else {
  console.log('Usage: embedding-provider.js [index|search <query>|serve [port]]');
}
