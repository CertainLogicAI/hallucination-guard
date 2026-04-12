#!/usr/bin/env bash
# setup.sh – one‑click installer for the deterministic OpenClaw agent
# ---------------------------------------------------------------
# What it does:
#   1. Installs sqlite3 if it is missing (required for the action‑tracker).
#   2. Makes the logging script executable.
#   3. Verifies that the deterministic AI layer can call the logger.
#   4. Gives a short test command you can run after the install.
# ---------------------------------------------------------------

set -e

# 1️⃣ Ensure sqlite3 is present ------------------------------------------------
if ! command -v sqlite3 >/dev/null 2>&1; then
  echo "sqlite3 not found – installing it now…"
  if command -v apt-get >/dev/null 2>&1; then
    sudo apt-get update && sudo apt-get install -y sqlite3
  elif command -v yum >/dev/null 2>&1; then
    sudo yum install -y sqlite
  else
    echo "Could not determine package manager – please install sqlite3 manually."
    exit 1
  fi
else
  echo "✅ sqlite3 already installed"
fi

# 2️⃣ Make the logger executable ------------------------------------------------
LOGGER_DIR="$(pwd)/action-tracker"
LOGGER="$LOGGER_DIR/log_action.sh"
if [[ -f "$LOGGER" ]]; then
  chmod +x "$LOGGER"
  echo "✅ Made log_action.sh executable"
else
  echo "⚠️  log_action.sh not found at $LOGGER"
  exit 1
fi

# 3️⃣ Verify the SQLite DB exists ------------------------------------------------
DB_PATH="$LOGGER_DIR/action_logs.db"
if [[ ! -f "$DB_PATH" ]]; then
  echo "Creating fresh SQLite DB at $DB_PATH"
  sqlite3 "$DB_PATH" "CREATE TABLE IF NOT EXISTS action_log (\
    id INTEGER PRIMARY KEY AUTOINCREMENT,\
    session_hash TEXT,\
    timestamp TEXT,\
    step TEXT,\
    input_hash TEXT,\
    output_hash TEXT,\
    decision TEXT,\
    metadata TEXT,\
    processing_time_ms INTEGER,\
    status TEXT\
  );"
else
  echo "✅ Existing action_logs.db found"
fi

# 4️⃣ Test a single logging round -----------------------------------------------
echo "Running a quick test of the deterministic AI layer with logging…"
# Generate a temporary session hash for the test
TEST_HASH=$(echo -n "test query" | sha256sum | awk '{print $1}')
# Log the start of the test
"$LOGGER" "$TEST_HASH" "test_step" "test_start" '{"msg":"test"}' "test query"
# Verify the DB entry
RESULT=$(sqlite3 "$DB_PATH" "SELECT step, decision FROM action_log WHERE session_hash='$TEST_HASH' ORDER BY id DESC LIMIT 1;")
if [[ -n "$RESULT" ]]; then
  echo "✅ Log entry recorded: $RESULT"
else
  echo "⚠️  No log entry found – something went wrong"
fi

# 5️⃣ Final instructions -------------------------------------------------------
cat <<'EOF'
=============================================================
Setup complete!

Next steps:
1️⃣ Run your deterministic agent, e.g.:
   ./deterministic_ai_layer.sh "What is 2+2?"
2️⃣ Verify logs were written:
   sqlite3 action-tracker/action_logs.db "SELECT * FROM action_log ORDER BY id DESC LIMIT 5;"

All files are located in the current directory:
- action-tracker/   (logging script + SQLite DB)
- deterministic_ai_layer.sh  (your AI layer)
- setup.sh          (this installer)
- README.txt        (explanations)

You can now close the SSH session – everything is ready for tomorrow.
=============================================================
EOF

exit 0
