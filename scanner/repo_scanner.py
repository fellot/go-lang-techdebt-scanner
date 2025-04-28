"""
Repository Scanner

Handles traversal of Go repositories and orchestrates the scanning process.
"""

import os
import subprocess
from metrics.complexity import ComplexityAnalyzer
from metrics.duplication import DuplicationAnalyzer
from metrics.test_quality import TestQualityAnalyzer
from metrics.dependencies import DependencyAnalyzer
from metrics.churn import ChurnAnalyzer
from metrics.readability import ReadabilityAnalyzer
from scoring.aggregator import ScoreAggregator

class RepoScanner:
    """Scanner for Go repositories."""
    
    def __init__(self, repo_path, config, verbose=False):
        """Initialize the repository scanner.
        
        Args:
            repo_path: Path to the Go repository
            config: Configuration dictionary
            verbose: Enable verbose output
        """
        self.repo_path = os.path.abspath(repo_path)
        self.config = config
        self.verbose = verbose
        
        # Initialize analyzers
        self.analyzers = {
            'complexity': ComplexityAnalyzer(config),
            'duplication': DuplicationAnalyzer(config),
            'test_quality': TestQualityAnalyzer(config),
            'dependencies': DependencyAnalyzer(config),
            'churn': ChurnAnalyzer(config),
            'readability': ReadabilityAnalyzer(config)
        }
        
        # Initialize score aggregator
        self.aggregator = ScoreAggregator(config)
        
        # Verify Go tools are installed
        self._verify_tools()
    
    def _verify_tools(self):
        """Verify that required Go tools are installed."""
        required_tools = [
            'go', 'gocyclo', 'gocognit', 'scc', 
            'golangci-lint', 'golint', 'git'
        ]
        
        missing_tools = []
        for tool in required_tools:
            try:
                subprocess.run(['which', tool], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE, 
                               check=True)
            except subprocess.CalledProcessError:
                missing_tools.append(tool)
        
        if missing_tools:
            print(f"Warning: The following tools are not installed: {', '.join(missing_tools)}")
            print("Some metrics may not be available.")
    
    def _find_go_files(self):
        """Find all Go files in the repository."""
        go_files = []
        for root, _, files in os.walk(self.repo_path):
            # Skip vendor and hidden directories
            if '/vendor/' in root or '/.' in root:
                continue
            
            for file in files:
                if file.endswith('.go'):
                    go_files.append(os.path.join(root, file))
        
        return go_files
    
    def scan(self):
        """Scan the repository and collect metrics."""
        if self.verbose:
            print("Starting repository scan...")
        
        # Find all Go files
        go_files = self._find_go_files()
        if self.verbose:
            print(f"Found {len(go_files)} Go files")
        
        # Collect metrics from each analyzer
        metrics = {}
        for name, analyzer in self.analyzers.items():
            if self.verbose:
                print(f"Running {name} analyzer...")
            metrics[name] = analyzer.analyze(self.repo_path, go_files)
        
        # Aggregate scores
        overall_score, category_scores = self.aggregator.aggregate(metrics)
        
        # Prepare results
        results = {
            'repo_path': self.repo_path,
            'overall_score': overall_score,
            'category_scores': category_scores,
            'metrics': metrics
        }
        
        return results