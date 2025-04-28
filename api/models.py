"""
API Models

Pydantic models for API requests and responses.
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, Any, Optional, List
import os

class ScanRequest(BaseModel):
    """Request model for repository scan."""
    repo_path: str = Field(..., description="Path to the Go repository")
    config_overrides: Optional[Dict[str, Any]] = Field(
        None, description="Optional configuration overrides"
    )
    
    @validator('repo_path')
    def validate_repo_path(cls, v):
        """Validate that the repository path exists."""
        if not os.path.isdir(v):
            raise ValueError(f"Repository path does not exist: {v}")
        return v

class CategoryScore(BaseModel):
    """Model for category scores."""
    score: float = Field(..., description="Normalized score (0-100)")
    level: str = Field(..., description="Debt level (LOW, MEDIUM, HIGH)")

class ScanResponse(BaseModel):
    """Response model for repository scan."""
    repo_path: str = Field(..., description="Path to the scanned repository")
    overall_score: float = Field(..., description="Overall technical debt score (0-100)")
    overall_level: str = Field(..., description="Overall debt level (LOW, MEDIUM, HIGH)")
    category_scores: Dict[str, CategoryScore] = Field(
        ..., description="Scores for each debt category"
    )
    metrics: Dict[str, Any] = Field(..., description="Detailed metrics for each category")

class ScanStatus(BaseModel):
    """Model for scan status."""
    status: str = Field(..., description="Status of the scan (pending, running, completed, failed)")
    scan_id: str = Field(..., description="Unique identifier for the scan")
    message: Optional[str] = Field(None, description="Additional status message")

class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    go_tools: Dict[str, bool] = Field(..., description="Availability of required Go tools")