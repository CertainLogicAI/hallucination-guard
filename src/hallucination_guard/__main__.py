#!/usr/bin/env python3
"""
Entry point for Hallucination Guard.
"""

import uvicorn
from .server import app

def main() -> None:
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()