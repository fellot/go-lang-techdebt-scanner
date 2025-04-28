"""
Readability Analyzer

Analyzes code readability and maintainability metrics.
"""

from scanner.go_tools import GoToolRunner
from scoring.normalizer import ScoreNormalizer
import os
import re

class ReadabilityAnalyzer:
    """Analyzer for code readability and maintainability."""
    
    def __init__(self, config):
        """Initialize the readability analyzer.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.normalizer = ScoreNormalizer()
    
    def analyze(self, repo_path, go_files):
        """Analyze code readability and maintainability.
        
        Args:
            repo_path: Path to the repository
            go_files: List of Go files
            
        Returns:
            Dictionary with readability metrics
        """
        # Run golint
        lint_results = GoToolRunner.run_golint(go_files)
        
        # Run gofmt
        fmt_results = GoToolRunner.run_gofmt(go_files)
        
        # Calculate metrics
        lint_issues_count = len(lint_results)
        fmt_issues_count = len(fmt_results)
        
        # Calculate issues per file
        lint_issues_per_file = lint_issues_count / max(1, len(go_files))
        fmt_issues_per_file = fmt_issues_count / max(1, len(go_files))
        
        # Calculate file metrics
        file_metrics = []
        for file_path in go_files:
            # Count lines
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.splitlines()
                
                # Count total lines
                total_lines = len(lines)
                
                # Count comment lines
                comment_lines = sum(1 for line in lines if line.strip().startswith('//') or line.strip().startswith('/*'))
                
                # Calculate comment ratio
                comment_ratio = comment_lines / max(1, total_lines)
                
                # Count function length
                function_lengths = []
                current_function_lines = 0
                in_function = False
                
                for line in lines:
                    line = line.strip()
                    if re.match(r'^func\s+', line) and '{' in line:
                        in_function = True
                        current_function_lines = 1
                    elif in_function:
                        current_function_lines += 1
                        if line == '}':
                            function_lengths.append(current_function_lines)
                            in_function = False
                
                # Calculate average function length
                avg_function_length = sum(function_lengths) / max(1, len(function_lengths))
                
                file_metrics.append({
                    'file': file_path,
                    'total_lines': total_lines,
                    'comment_lines': comment_lines,
                    'comment_ratio': comment_ratio,
                    'function_count': len(function_lengths),
                    'avg_function_length': avg_function_length
                })
        
        # Calculate averages across all files
        avg_comment_ratio = sum(m['comment_ratio'] for m in file_metrics) / max(1, len(file_metrics))
        avg_function_length = sum(m['avg_function_length'] for m in file_metrics) / max(1, len(file_metrics))
        
        # Calculate normalized scores (0-100, where 0 is best)
        lint_score = self.normalizer.normalize_count(
            lint_issues_per_file,
            self.config['readability']['ideal_lint_issues'],
            self.config['readability']['worst_lint_issues']
        )
        
        fmt_score = self.normalizer.normalize_count(
            fmt_issues_per_file,
            self.config['readability']['ideal_fmt_issues'],
            self.config['readability']['worst_fmt_issues']
        )
        
        comment_score = self.normalizer.normalize_inverse_percentage(
            avg_comment_ratio * 100,
            self.config['readability']['ideal_comment_ratio'],
            self.config['readability']['worst_comment_ratio']
        )
        
        function_length_score = self.normalizer.normalize_count(
            avg_function_length,
            self.config['readability']['ideal_function_length'],
            self.config['readability']['worst_function_length']
        )
        
        # Calculate overall readability score
        weights = self.config['readability']
        overall_score = (
            lint_score * weights['lint_weight'] +
            fmt_score * weights['fmt_weight'] +
            comment_score * weights['comment_weight'] +
            function_length_score * weights['function_length_weight']
        ) / (
            weights['lint_weight'] +
            weights['fmt_weight'] +
            weights['comment_weight'] +
            weights['function_length_weight']
        )
        
        return {
            'lint_issues': lint_issues_count,
            'fmt_issues': fmt_issues_count,
            'lint_issues_per_file': lint_issues_per_file,
            'fmt_issues_per_file': fmt_issues_per_file,
            'avg_comment_ratio': avg_comment_ratio,
            'avg_function_length': avg_function_length,
            'file_metrics': file_metrics,
            'lint_score': lint_score,
            'fmt_score': fmt_score,
            'comment_score': comment_score,
            'function_length_score': function_length_score,
            'score': overall_score
        }