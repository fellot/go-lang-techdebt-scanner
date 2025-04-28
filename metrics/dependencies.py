"""
Dependency Analyzer

Analyzes dependency health including outdated and vulnerable dependencies.
"""

from scanner.go_tools import GoToolRunner
from scoring.normalizer import ScoreNormalizer
import subprocess
import json

class DependencyAnalyzer:
    """Analyzer for dependency health."""
    
    def __init__(self, config):
        """Initialize the dependency analyzer.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.normalizer = ScoreNormalizer()
    
    def analyze(self, repo_path, go_files):
        """Analyze dependency health.
        
        Args:
            repo_path: Path to the repository
            go_files: List of Go files
            
        Returns:
            Dictionary with dependency metrics
        """
        # Analyze dependencies
        dependency_info = GoToolRunner.analyze_dependencies(repo_path)
        
        if 'error' in dependency_info:
            # Not a Go module
            return {
                'is_module': False,
                'dependency_count': 0,
                'outdated_count': 0,
                'outdated_percentage': 0,
                'vulnerable_count': 0,
                'score': 0  # No dependencies, no debt
            }
        
        # Count dependencies
        dependency_count = len(dependency_info['dependencies'])
        
        # Count outdated dependencies
        outdated_count = len(dependency_info['outdated'])
        outdated_percentage = (outdated_count / max(1, dependency_count)) * 100
        
        # Check for vulnerable dependencies using govulncheck if available
        vulnerable_deps = []
        try:
            cmd = ['govulncheck', './...']
            result = subprocess.run(
                cmd,
                cwd=repo_path,
                capture_output=True,
                text=True
            )
            
            # Parse govulncheck output (simplified)
            for line in result.stdout.splitlines():
                if 'vulnerability' in line.lower():
                    vulnerable_deps.append(line)
        except (subprocess.SubprocessError, FileNotFoundError):
            # govulncheck not available
            pass
        
        vulnerable_count = len(vulnerable_deps)
        
        # Calculate normalized scores (0-100, where 0 is best)
        outdated_score = self.normalizer.normalize_percentage(
            outdated_percentage,
            self.config['dependencies']['ideal_outdated'],
            self.config['dependencies']['worst_outdated']
        )
        
        vulnerable_score = self.normalizer.normalize_count(
            vulnerable_count,
            0,  # Ideal: no vulnerabilities
            self.config['dependencies']['worst_vulnerabilities']
        )
        
        # Calculate overall dependency health score
        overall_score = (
            outdated_score * self.config['dependencies']['outdated_weight'] +
            vulnerable_score * self.config['dependencies']['vulnerable_weight']
        ) / (
            self.config['dependencies']['outdated_weight'] +
            self.config['dependencies']['vulnerable_weight']
        )
        
        return {
            'is_module': True,
            'dependency_count': dependency_count,
            'dependencies': dependency_info['dependencies'],
            'outdated_count': outdated_count,
            'outdated_percentage': outdated_percentage,
            'outdated_dependencies': dependency_info['outdated'],
            'vulnerable_count': vulnerable_count,
            'vulnerable_dependencies': vulnerable_deps,
            'outdated_score': outdated_score,
            'vulnerable_score': vulnerable_score,
            'score': overall_score
        }