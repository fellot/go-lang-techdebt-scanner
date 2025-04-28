"""
Complexity Analyzer

Analyzes code complexity metrics including cyclomatic and cognitive complexity.
"""

from scanner.go_tools import GoToolRunner
from scoring.normalizer import ScoreNormalizer

class ComplexityAnalyzer:
    """Analyzer for code complexity metrics."""
    
    def __init__(self, config):
        """Initialize the complexity analyzer.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.normalizer = ScoreNormalizer()
        
        # Get thresholds from config
        self.cyclomatic_threshold = config.get('complexity', {}).get('cyclomatic_threshold', 15)
        self.cognitive_threshold = config.get('complexity', {}).get('cognitive_threshold', 15)
    
    def analyze(self, repo_path, go_files):
        """Analyze code complexity.
        
        Args:
            repo_path: Path to the repository
            go_files: List of Go files
            
        Returns:
            Dictionary with complexity metrics
        """
        # Run gocyclo
        cyclomatic_results = GoToolRunner.run_gocyclo(
            repo_path, 
            threshold=self.cyclomatic_threshold
        )
        
        # Run gocognit
        cognitive_results = GoToolRunner.run_gocognit(
            repo_path, 
            threshold=self.cognitive_threshold
        )
        
        # Calculate metrics
        cyclomatic_avg = cyclomatic_results['average_complexity']
        cognitive_avg = cognitive_results['average_complexity']
        
        # Count functions exceeding thresholds
        cyclomatic_violations = len(cyclomatic_results['functions'])
        cognitive_violations = len(cognitive_results['functions'])
        
        # Find worst offenders
        cyclomatic_offenders = sorted(
            cyclomatic_results['functions'], 
            key=lambda x: x['complexity'], 
            reverse=True
        )[:10]
        
        cognitive_offenders = sorted(
            cognitive_results['functions'], 
            key=lambda x: x['complexity'], 
            reverse=True
        )[:10]
        
        # Calculate normalized scores (0-100, where 0 is best)
        cyclomatic_score = self.normalizer.normalize_complexity(
            cyclomatic_avg, 
            self.config['complexity']['cyclomatic_ideal'],
            self.config['complexity']['cyclomatic_worst']
        )
        
        cognitive_score = self.normalizer.normalize_complexity(
            cognitive_avg, 
            self.config['complexity']['cognitive_ideal'],
            self.config['complexity']['cognitive_worst']
        )
        
        # Calculate overall complexity score
        overall_score = (
            cyclomatic_score * self.config['complexity']['cyclomatic_weight'] +
            cognitive_score * self.config['complexity']['cognitive_weight']
        ) / (
            self.config['complexity']['cyclomatic_weight'] +
            self.config['complexity']['cognitive_weight']
        )
        
        return {
            'cyclomatic': {
                'average': cyclomatic_avg,
                'violations': cyclomatic_violations,
                'worst_offenders': cyclomatic_offenders,
                'score': cyclomatic_score
            },
            'cognitive': {
                'average': cognitive_avg,
                'violations': cognitive_violations,
                'worst_offenders': cognitive_offenders,
                'score': cognitive_score
            },
            'overall_score': overall_score
        }