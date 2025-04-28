"""
Test Quality Analyzer

Analyzes test coverage and quality metrics.
"""

import os
from scanner.go_tools import GoToolRunner
from scoring.normalizer import ScoreNormalizer

class TestQualityAnalyzer:
    """Analyzer for test coverage and quality."""
    
    def __init__(self, config):
        """Initialize the test quality analyzer.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.normalizer = ScoreNormalizer()
    
    def analyze(self, repo_path, go_files):
        """Analyze test coverage and quality.
        
        Args:
            repo_path: Path to the repository
            go_files: List of Go files
            
        Returns:
            Dictionary with test quality metrics
        """
        # Run go test with coverage
        coverage_data = GoToolRunner.run_go_test(repo_path)
        
        # Calculate coverage metrics
        total_files = len(go_files)
        files_with_tests = 0
        total_coverage = 0.0
        
        # Count test files
        test_files = [f for f in go_files if os.path.basename(f).endswith('_test.go')]
        test_file_count = len(test_files)
        
        # Calculate coverage percentage
        covered_files = []
        uncovered_files = []
        
        for file_path in go_files:
            # Skip test files
            if file_path.endswith('_test.go'):
                continue
                
            # Check if file has coverage data
            rel_path = os.path.relpath(file_path, repo_path)
            if rel_path in coverage_data:
                files_with_tests += 1
                
                # Parse coverage info
                coverage_info = coverage_data[rel_path]
                # This is simplified; actual parsing would be more complex
                file_coverage = 70.0  # Placeholder
                
                total_coverage += file_coverage
                
                covered_files.append({
                    'file': rel_path,
                    'coverage': file_coverage
                })
            else:
                uncovered_files.append(rel_path)
        
        # Calculate average coverage
        avg_coverage = total_coverage / max(1, files_with_tests)
        
        # Calculate test-to-code ratio
        test_to_code_ratio = test_file_count / max(1, total_files - test_file_count)
        
        # Calculate normalized scores (0-100, where 0 is best)
        coverage_score = self.normalizer.normalize_inverse_percentage(
            avg_coverage,
            self.config['test_quality']['ideal_coverage'],
            self.config['test_quality']['worst_coverage']
        )
        
        ratio_score = self.normalizer.normalize_ratio(
            test_to_code_ratio,
            self.config['test_quality']['ideal_ratio'],
            self.config['test_quality']['worst_ratio']
        )
        
        # Calculate overall test quality score
        overall_score = (
            coverage_score * self.config['test_quality']['coverage_weight'] +
            ratio_score * self.config['test_quality']['ratio_weight']
        ) / (
            self.config['test_quality']['coverage_weight'] +
            self.config['test_quality']['ratio_weight']
        )
        
        return {
            'test_file_count': test_file_count,
            'files_with_tests': files_with_tests,
            'files_without_tests': len(uncovered_files),
            'average_coverage': avg_coverage,
            'test_to_code_ratio': test_to_code_ratio,
            'covered_files': covered_files,
            'uncovered_files': uncovered_files,
            'coverage_score': coverage_score,
            'ratio_score': ratio_score,
            'overall_score': overall_score
        }