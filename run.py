#!/usr/bin/env python3
"""
Simple run script for the Smart Task Planner.
Usage: python run.py
"""
import uvicorn
import os
import sys
from pathlib import Path

# Add project root to path
root = Path(__file__).parent
sys.path.insert(0, str(root))

# Change to project root directory so relative paths work
os.chdir(str(root))

if __name__ == "__main__":
    print("Starting Smart Task Planner...")
    print("Visit http://localhost:8000 in your browser")
    print("Set GROQ_API_KEY environment variable to use Groq (optional)")
    print("Press Ctrl+C to stop")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
