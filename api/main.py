#!/usr/bin/env python3
"""
Log Backup API - Provides REST endpoints for log retrieval and backup operations.
"""
import os
import subprocess
import tarfile
import tempfile
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

app = FastAPI(
    title="Log Backup API",
    description="REST API for log retrieval, status, and backup operations",
    version="1.0.0"
)

# Configuration
BASE_DIR = Path("/data/.openclaw/workspace")
LOGS_DIR = BASE_DIR / "conversation_logs"
MEMORY_DIR = BASE_DIR / "memory"
ARCHIVE_DIR = MEMORY_DIR / "archive"

# Ensure directories exist
ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)


class BackupRequest(BaseModel):
    """Request model for backup operations"""
    verbose: bool = False
    compress: bool = True


class StatusResponse(BaseModel):
    """Response model for status endpoint"""
    logs_count: int
    archives_count: int
    memory_size_bytes: int
    timestamp: str


@app.get("/", tags=["Health"])
def root():
    """Root endpoint - returns API info"""
    return {
        "service": "Log Backup API",
        "version": "1.0.0",
        "status": "operational"
    }


@app.get("/status", response_model=StatusResponse, tags=["Status"])
def status():
    """
    Return quick health info about the log system.
    """
    logs_count = len(list(LOGS_DIR.glob("*.md")))
    archives_count = len(list(ARCHIVE_DIR.glob("*.tar.gz")))
    
    memory_file = MEMORY_DIR / "MEMORY.md"
    memory_size = memory_file.stat().st_size if memory_file.exists() else 0
    
    return StatusResponse(
        logs_count=logs_count,
        archives_count=archives_count,
        memory_size_bytes=memory_size,
        timestamp=datetime.utcnow().isoformat() + "Z"
    )


@app.get("/logs/{msg_id}", tags=["Logs"])
def get_log(msg_id: str):
    """
    Retrieve a specific log file (original markdown).
    
    Searches in order:
    1. Hot logs (conversation_logs/)
    2. Compressed archives
    """
    # 1) Search hot logs
    file_candidate = LOGS_DIR / f"{msg_id}.md"
    if file_candidate.is_file():
        return FileResponse(
            str(file_candidate),
            media_type="text/markdown",
            filename=f"{msg_id}.md"
        )

    # 2) Search archives
    for archive in ARCHIVE_DIR.glob("*.tar.gz"):
        try:
            with tarfile.open(archive, "r:gz") as tar:
                members = [m for m in tar.getmembers() if m.name == f"{msg_id}.md"]
                if members:
                    # Extract to temp file
                    with tempfile.NamedTemporaryFile(mode='w+b', suffix=".md", delete=False) as tmp:
                        tmp_path = tmp.name
                        extracted = tar.extractfile(members[0])
                        if extracted:
                            tmp.write(extracted.read())
                    return FileResponse(
                        tmp_path,
                        media_type="text/markdown",
                        filename=f"{msg_id}.md"
                    )
        except Exception:
            continue

    raise HTTPException(status_code=404, detail=f"Log {msg_id} not found")


@app.post("/backup-now", tags=["Backup"])
def backup_now(req: BackupRequest = BackupRequest()):
    """
    Trigger compression and backup of current logs.
    
    Creates a new archive in the archive directory.
    If cloud backup is configured (rclone), syncs to cloud.
    """
    if not req.compress:
        return {"msg": "Compression disabled", "action": "skipped"}
    
    timestamp = int(datetime.utcnow().timestamp())
    archive_name = f"backup_{timestamp}.tar.gz"
    archive_path = ARCHIVE_DIR / archive_name
    
    # Create tar.gz of current logs
    try:
        with tarfile.open(archive_path, "w:gz") as tar:
            logs = list(LOGS_DIR.glob("*.md"))
            for log_file in logs:
                tar.add(log_file, arcname=log_file.name)
        
        archive_size = archive_path.stat().st_size
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Compression failed: {str(e)}")
    
    result = {
        "msg": "Backup completed",
        "archive": str(archive_path),
        "archive_size_bytes": archive_size,
        "logs_archived": len(logs),
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    # Attempt cloud sync if configured (optional)
    try:
        rclone_config = BASE_DIR / "rclone.conf"
        if rclone_config.exists():
            result_sync = subprocess.run(
                ["rclone", "sync", str(ARCHIVE_DIR), "b2logs:archive", "-v"],
                capture_output=True,
                timeout=300
            )
            result["cloud_sync"] = "success" if result_sync.returncode == 0 else "failed"
        else:
            result["cloud_sync"] = "not_configured"
    except Exception as e:
        result["cloud_sync"] = f"error: {str(e)}"
    
    if req.verbose:
        result["details"] = f"Created archive with {len(logs)} files"
    
    return result


@app.get("/archives", tags=["Archives"])
def list_archives():
    """
    List all available archives.
    """
    archives = []
    for archive in sorted(ARCHIVE_DIR.glob("*.tar.gz")):
        stat = archive.stat()
        archives.append({
            "name": archive.name,
            "size_bytes": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat() + "Z"
        })
    return {"archives": archives}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
# Health endpoint
@app.get("/health", tags=["Health"])
def health_check():
    import subprocess, os
    # check daemon process
    try:
        out = subprocess.check_output(['pgrep','-f','sync_daemon.sh']).decode().strip()
        daemon_running = bool(out)
    except Exception:
        daemon_running = False
    logs_ok = os.path.isdir(str(LOGS_DIR)) and os.access(str(LOGS_DIR), os.W_OK)
    ready = daemon_running and logs_ok
    return {
        "ready": ready,
        "daemon_running": daemon_running,
        "logs_directory": str(LOGS_DIR),
        "logs_writable": logs_ok,
        "timestamp": datetime.utcnow().isoformat()+"Z"
    }
