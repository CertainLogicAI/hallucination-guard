-- Graph Schema for Memory Files
-- SQLite-based knowledge graph for relationship-based search

-- Entities (nodes)
CREATE TABLE IF NOT EXISTS entities (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  type TEXT NOT NULL,          -- 'person', 'project', 'domain', 'tech', 'concept', 'file'
  name TEXT NOT NULL,          -- normalized name for deduplication
  display_name TEXT,           -- human-readable name
  metadata TEXT,               -- JSON for extra info
  source_file TEXT,            -- where this entity was first extracted
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(type, name)
);

-- Relationships (edges)
CREATE TABLE IF NOT EXISTS relationships (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  from_entity_id INTEGER NOT NULL,
  to_entity_id INTEGER NOT NULL,
  type TEXT NOT NULL,          -- 'mentioned_in', 'worked_on', 'uses_tech', 'has_concept', 'owns_domain', etc.
  strength REAL DEFAULT 1.0,   -- confidence/importance weight
  snippet TEXT,                -- excerpt from source showing relationship
  source_file TEXT NOT NULL,
  line_number INTEGER,
  extracted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (from_entity_id) REFERENCES entities(id),
  FOREIGN KEY (to_entity_id) REFERENCES entities(id)
);

-- Full-text search index for quick relationship lookup
CREATE VIRTUAL TABLE IF NOT EXISTS relationship_fts USING fts5(
  snippet,
  source_file,
  metadata
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_entities_type_name ON entities(type, name);
CREATE INDEX IF NOT EXISTS idx_relationships_type ON relationships(type);
CREATE INDEX IF NOT EXISTS idx_relationships_from ON relationships(from_entity_id);
CREATE INDEX IF NOT EXISTS idx_relationships_to ON relationships(to_entity_id);