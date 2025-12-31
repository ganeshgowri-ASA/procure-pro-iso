"""
Main entry point for Procure-Pro-ISO TBE Scoring Engine.

Run with: uvicorn main:app --reload
"""

import uvicorn

from src.api.app import app

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
