#!/usr/bin/env python3
"""
Go Technical Debt Scanner - FastAPI Service

This service analyzes Go repositories for technical debt and returns a comprehensive JSON report.
"""

import os
import yaml
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router

# Create FastAPI app
app = FastAPI(
    title="Go Technical Debt Scanner API",
    description="API for analyzing technical debt in Go repositories",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include API routes
app.include_router(router)

# Load configuration
@app.on_event("startup")
async def startup_event():
    try:
        with open("config.yaml", "r") as f:
            app.state.config = yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading configuration: {e}")
        # Use default configuration if file not found
        app.state.config = {
            "thresholds": {"high": 70, "medium": 40, "low": 0},
            "weights": {
                "complexity": 1.5, "duplication": 1.0, "test_quality": 1.5,
                "dependencies": 1.0, "churn": 0.8, "readability": 1.2
            },
            # Add other default configurations...
        }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)