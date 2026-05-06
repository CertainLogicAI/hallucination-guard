---
allowed_ops: brain.put_page, brain.get_page, brain.query
forbidden_ops: brain.sync, brain.ingest
required_fields: source
---
Medical: agents can read/write records but cannot bulk-sync.
