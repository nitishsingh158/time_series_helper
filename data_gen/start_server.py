#!/usr/bin/env python3
"""
Startup script for the Asset Data Server
"""

import uvicorn
from main import app

if __name__ == "__main__":
    print("🚀 Starting Asset Data Server...")
    print(
        "📊 Server will provide data for 15 assets with 3 months of 5-minute interval data"
    )
    print("🌐 API Documentation available at: http://localhost:8000/docs")
    print("📖 ReDoc Documentation available at: http://localhost:8000/redoc")
    print("🔗 Base URL: http://localhost:8000")
    print("\nEndpoints:")
    print("  GET /scan - List all available assets")
    print("  GET /timeseries?asset_key=<ASSET_KEY> - Get timeseries data")
    print("\nPress Ctrl+C to stop the server\n")

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info", access_log=True)
