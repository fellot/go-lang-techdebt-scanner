"""
Scanning Service

Service layer for repository scanning.
"""

import os
import asyncio
import subprocess
from typing import Dict, Any, List
from scanner.repo_scanner import RepoScanner
from scoring.thresholds import DebtThresholds

async def scan_repository(repo_path: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Scan a repository for technical debt.
    
    Args:
        repo_path: Path to the repository
        config: Configuration dictionary
        
    Returns:
        Dictionary with scan results
    """
    # Run the scan in a separate thread to avoid blocking
    loop = asyncio.get_event_loop()
    results = await loop.run_in_executor(
        None,
        lambda: _run_scan(repo_path, config)
    )
    
    return results

def _run_scan(repo_path: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run the scan synchronously.
    
    Args:
        repo_path: Path to the repository
        config: Configuration dictionary
        
    Returns:
        Dictionary with scan results
    """
    # Initialize scanner
    scanner = RepoScanner(repo_path, config, verbose=True)
    
    # Run scan
    results = scanner.scan()
    
    # Add debt levels to category scores
    thresholds = DebtThresholds(config)
    category_scores = {}
    for category, score in results['category_scores'].items():
        level = thresholds.get_debt_level(score)
        category_scores[category] = {
            "score": score,
            "level": level.upper()
        }
    
    # Determine overall debt level
    overall_level = thresholds.get_debt_level(results['overall_score']).upper()
    
    # Prepare final results
    final_results = {
        "repo_path": repo_path,
        "overall_score": results['overall_score'],
        "overall_level": overall_level,
        "category_scores": category_scores,
        "metrics": results['metrics']
    }
    
    return final_results

def check_go_tools() -> Dict[str, bool]:
    """
    Check if required Go tools are installed.
    
    Returns:
        Dictionary with tool availability
    """
    required_tools = [
        'go', 'gocyclo', 'gocognit', 'scc', 
        'golangci-lint', 'golint', 'git'
    ]
    
    tool_availability = {}
    for tool in required_tools:
        try:
            subprocess.run(
                ['which', tool], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                check=True
            )
            tool_availability[tool] = True
        except subprocess.CalledProcessError:
            tool_availability[tool] = False
    
    return tool_availability