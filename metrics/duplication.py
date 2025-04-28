"""
Duplication Analyzer

Analyzes code duplication using SCC tool.
"""

from scanner.go_tools import GoToolRunner
from scoring.normalizer import ScoreNormalizer

class DuplicationAnalyzer:
    """Analyzer for code duplication."""
    
    def __init__(self, config):
        """Initialize the duplication analyzer.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.normalizer = ScoreNormalizer()
    
    def analyze(self, repo_path, go_files):
        """Analyze code duplication.
        
        Args:
            repo_path: Path to the repository
            go_files: List of Go files
            
        Returns:
            Dictionary with duplication metrics
        """
        # Run SCC to get complexity and duplication metrics
        scc_results = GoToolRunner.run_scc(repo_path)
        
        # Calculate total lines and duplicated lines
        total_lines = 0
        duplicated_lines = 0
        
        for file_result in scc_results:
            total_lines += file_result.get('Code', 0)
            duplicated_lines += file_result.get('Duplicate', 0)
        
        # Calculate duplication percentage
        duplication_percentage = (duplicated_lines / max(1, total_lines)) * 100
        
        # Find files with highest duplication
        files_with_duplication = []
        for file_result in scc_results:
            if file_result.get('Duplicate', 0) > 0:
                dup_percentage = (file_result.get('Duplicate', 0) / 
                                 max(1, file_result.get('Code', 0))) * 100
                files_with_duplication.append({
                    'file': file_result.get('Location', ''),
                    'duplicated_lines': file_result.get('Duplicate', 0),
                    'total_lines': file_result.get('Code', 0),
                    'percentage': dup_percentage
                })
        
        # Sort by percentage of duplication
        files_with_duplication.sort(key=lambda x: x['percentage'], reverse=True)
        
        # Calculate normalized score (0-100, where 0 is best)
        duplication_score = self.normalizer.normalize_percentage(
            duplication_percentage,
            self.config['duplication']['ideal_percentage'],
            self.config['duplication']['worst_percentage']
        )
        
        return {
            'total_lines': total_lines,
            'duplicated_lines': duplicated_lines,
            'duplication_percentage': duplication_percentage,
            'files_with_duplication': files_with_duplication[:10],  # Top 10
            'score': duplication_score
        }