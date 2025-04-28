"""
API Routes

FastAPI routes for the technical debt scanner API.
"""

from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends, Request
from typing import Dict, Any, List
import uuid
import os
from .models import ScanRequest, ScanResponse, ScanStatus, HealthResponse
from .services import scan_repository, check_go_tools

# Create router
router = APIRouter()

# Store for scan results (in-memory for simplicity, use a database in production)
scan_results = {}

@router.post("/scan", response_model=ScanStatus, status_code=202)
async def start_scan(
    request: ScanRequest, 
    background_tasks: BackgroundTasks,
    req: Request
):
    """
    Start a technical debt scan for a Go repository.
    
    Returns a scan ID that can be used to check the status and retrieve results.
    """
    # Generate a unique scan ID
    scan_id = str(uuid.uuid4())
    
    # Store initial status
    scan_results[scan_id] = {
        "status": "pending",
        "repo_path": request.repo_path,
        "message": "Scan queued"
    }
    
    # Get configuration
    config = req.app.state.config
    if request.config_overrides:
        # Deep merge the overrides
        for category, values in request.config_overrides.items():
            if category in config and isinstance(values, dict):
                config[category].update(values)
            else:
                config[category] = values
    
    # Start scan in background
    background_tasks.add_task(
        run_scan_task, 
        scan_id=scan_id,
        repo_path=request.repo_path,
        config=config
    )
    
    return {
        "status": "pending",
        "scan_id": scan_id,
        "message": "Scan started"
    }

@router.get("/scan/{scan_id}", response_model=Dict[str, Any])
async def get_scan_result(scan_id: str):
    """
    Get the results or status of a technical debt scan.
    
    If the scan is complete, returns the full results.
    If the scan is still running, returns the current status.
    """
    if scan_id not in scan_results:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    return scan_results[scan_id]

@router.get("/scans", response_model=Dict[str, Dict[str, Any]])
async def list_scans():
    """
    List all scans and their statuses.
    """
    return {
        scan_id: {
            "status": data.get("status", "unknown"),
            "repo_path": data.get("repo_path", ""),
            "message": data.get("message", "")
        }
        for scan_id, data in scan_results.items()
    }

@router.delete("/scan/{scan_id}", status_code=204)
async def delete_scan(scan_id: str):
    """
    Delete a scan result.
    """
    if scan_id not in scan_results:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    del scan_results[scan_id]
    return None

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Check the health of the service and required Go tools.
    """
    go_tools = check_go_tools()
    
    return {
        "status": "healthy",
        "version": "1.0.0",
        "go_tools": go_tools
    }

async def run_scan_task(scan_id: str, repo_path: str, config: Dict[str, Any]):
    """
    Run the technical debt scan in the background.
    """
    try:
        # Update status to running
        scan_results[scan_id]["status"] = "running"
        scan_results[scan_id]["message"] = "Scan in progress"
        
        # Run the scan
        results = await scan_repository(repo_path, config)
        
        # Update with results
        scan_results[scan_id] = {
            "status": "completed",
            "repo_path": repo_path,
            "message": "Scan completed successfully",
            **results
        }
    except Exception as e:
        # Update with error
        scan_results[scan_id] = {
            "status": "failed",
            "repo_path": repo_path,
            "message": f"Scan failed: {str(e)}"
        }