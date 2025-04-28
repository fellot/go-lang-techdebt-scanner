"""
Code Churn Analyzer

Analyzes code churn and stability metrics.
"""

from scanner.git_analyzer import GitAnalyzer
from scoring.normalizer import ScoreNormalizer

class ChurnAnalyzer:
    """Analyzer for code churn and stability."""
    
    def __init__(self, config):
        """Initialize the churn analyzer.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.normalizer = ScoreNormalizer()
    
    def analyze(self, repo_path, go_files):
        """Analyze code churn and stability.
        
        Args:
            repo_path: Path to the repository
            go_files: List of Go files
            
        Returns:
            Dictionary with churn metrics
        """
        # Initialize Git analyzer
        git_analyzer = GitAnalyzer(repo_path)
        
        # Get repository-level churn
        repo_churn = git_analyzer.get_repo_churn(
            days=self.config['churn']['analysis_period_days']
        )
        
        # Get file-level churn for each Go file
        file_churn = {}
        for file_path in go_files:
            file_churn[file_path] = git_analyzer.get_file_churn(
                file_path,
                days=self.config['churn']['analysis_period_days']
            )
        
        # Calculate average churn rate across files
        total_churn_rate = sum(data['churn_rate'] for data in file_churn.values())
        avg_churn_rate = total_churn_rate / max(1, len(file_churn))
        
        # Identify files with highest churn
        high_churn_files = []
        for file_path, data in file_churn.items():
            if data['churn_rate'] > 0:
                high_churn_files.append({
                    'file': file_path,
                    'churn_rate': data['churn_rate'],
                    'commits': data['commits'],
                    'additions': data['additions'],
                    'deletions': data['deletions']
                })
        
        # Sort by churn rate
        high_churn_files.sort(key=lambda x: x['churn_rate'], reverse=True)
        
        # Calculate normalized score (0-100, where 0 is best)
        churn_score = self.normalizer.normalize_churn(
            avg_churn_rate,
            self.config['churn']['ideal_churn_rate'],
            self.config['churn']['worst_churn_rate']
        )
        
        return {
            'repository_churn': repo_churn,
            'average_churn_rate': avg_churn_rate,
            'high_churn_files': high_churn_files[:10],  # Top 10
            'score': churn_score
        }