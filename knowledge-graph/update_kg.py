#!/usr/bin/env python3
"""Update a simple knowledge‑graph SQLite DB from memory files.

- Every Markdown file under the workspace (MEMORY.md and daily notes) becomes a node.
- The file name (without extension) is used as the node title.
- Optional front‑matter tags are read from a YAML block at the top of the file.
- Links of the form ``[[OtherFile]]`` generate directed edges of type "links".

The script is idempotent: it inserts new nodes/edges and updates ``updated_at``
when a file's modification time changes.
"""
import os, re, sys, sqlite3, time, yaml, hashlib

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DB_PATH = os.path.join(os.path.dirname(__file__), "graph.db")

def init_db(conn):
    cur = conn.cursor()
    cur.executescript('''
        CREATE TABLE IF NOT EXISTS nodes (
            id INTEGER PRIMARY KEY,
            path TEXT UNIQUE,
            title TEXT,
            tags TEXT,
            mtime REAL,
            checksum TEXT,
            updated_at REAL
        );
        CREATE TABLE IF NOT EXISTS edges (
            id INTEGER PRIMARY KEY,
            src INTEGER,
            dst INTEGER,
            type TEXT,
            UNIQUE(src, dst, type)
        );
        CREATE INDEX IF NOT EXISTS idx_nodes_path ON nodes(path);
        CREATE INDEX IF NOT EXISTS idx_edges_src ON edges(src);
    ''')
    conn.commit()

def file_checksum(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()

def parse_frontmatter(text):
    # Front‑matter is a YAML block delimited by --- at start and end
    if not text.startswith('---'):
        return {}, text
    end = text.find('\n---', 3)
    if end == -1:
        return {}, text
    fm = text[3:end]
    rest = text[end+4:]
    try:
        data = yaml.safe_load(fm)
    except Exception:
        data = {}
    return data or {}, rest

def extract_links(text):
    # Markdown wiki‑style links [[FileName]]
    return re.findall(r'\[\[([^\]]+)\]\]', text)

def main():
    conn = sqlite3.connect(DB_PATH)
    init_db(conn)
    cur = conn.cursor()
    # Walk all markdown files in workspace (skip hidden dirs)
    for dirpath, _, filenames in os.walk(ROOT):
        for fn in filenames:
            if not fn.lower().endswith('.md'):
                continue
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, ROOT)
            mtime = os.path.getmtime(full)
            checksum = file_checksum(full)
            # Check if node exists and up‑to‑date
            cur.execute('SELECT id, mtime, checksum FROM nodes WHERE path=?', (rel,))
            row = cur.fetchone()
            with open(full, 'r', encoding='utf-8') as f:
                content = f.read()
            fm, body = parse_frontmatter(content)
            title = fm.get('title') or os.path.splitext(fn)[0]
            tags = ','.join(fm.get('tags', [])) if isinstance(fm.get('tags'), list) else str(fm.get('tags') or '')
            if row:
                nid, old_mtime, old_checksum = row
                if old_checksum == checksum:
                    # No change – skip edge recompute
                    continue
                # Update node
                cur.execute('UPDATE nodes SET title=?, tags=?, mtime=?, checksum=?, updated_at=? WHERE id=?',
                            (title, tags, mtime, checksum, time.time(), nid))
            else:
                cur.execute('INSERT INTO nodes (path, title, tags, mtime, checksum, updated_at) VALUES (?,?,?,?,?,?)',
                            (rel, title, tags, mtime, checksum, time.time()))
                nid = cur.lastrowid
            # Re‑compute edges for this file
            # First delete existing outgoing edges
            cur.execute('DELETE FROM edges WHERE src=?', (nid,))
            links = extract_links(body)
            for link in links:
                # Resolve link to a path – assume same directory or .md extension
                target = link
                if not target.lower().endswith('.md'):
                    target += '.md'
                # Simple resolution: look for file anywhere under ROOT
                target_path = None
                for dir2, _, files2 in os.walk(ROOT):
                    if target in files2:
                        target_path = os.path.relpath(os.path.join(dir2, target), ROOT)
                        break
                if target_path:
                    # ensure target node exists (or will be created later)
                    cur.execute('SELECT id FROM nodes WHERE path=?', (target_path,))
                    tgt_row = cur.fetchone()
                    if tgt_row:
                        dst_id = tgt_row[0]
                    else:
                        # placeholder node – minimal info
                        cur.execute('INSERT OR IGNORE INTO nodes (path, title, tags, mtime, checksum, updated_at) VALUES (?,?,?,?,?,?)',
                                    (target_path, os.path.splitext(target)[0], '', 0, '', time.time()))
                        dst_id = cur.lastrowid
                    cur.execute('INSERT OR IGNORE INTO edges (src, dst, type) VALUES (?,?,?)', (nid, dst_id, 'links'))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    main()
