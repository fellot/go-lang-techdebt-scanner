"""
Score Aggregator

Aggregates individual metric scores into category and overall scores.
"""

class ScoreAggregator:
    """Aggregates individual metric scores."""
    
    def __init__(self, config):
        """Initialize the score aggregator.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
    
    def aggregate(self, metrics):
        """Aggregate individual metric scores into category and overall scores.
        
        Args:
            metrics: Dictionary with metrics from all analyzers
            
        Returns:
            Tuple of (overall_score, category_scores)
        """
        # Extract category scores
        category_scores = {
            'complexity': metrics['complexity']['overall_score'],
            'duplication': metrics['duplication']['score'],
            'test_quality': metrics['test_quality']['overall_score'],
            'dependencies': metrics['dependencies']['score'],
            'churn': metrics['churn']['score'],
            'readability': metrics['readability']['score']
        }
        
        # Calculate overall score using weights from config
        weights = self.config['weights']
        overall_score = (
            category_scores['complexity'] * weights['complexity'] +
            category_scores['duplication'] * weights['duplication'] +
            category_scores['test_quality'] * weights['test_quality'] +
            category_scores['dependencies'] * weights['dependencies'] +
            category_scores['churn'] * weights['churn'] +
            category_scores['readability'] * weights['readability']
        ) / sum(weights.values())
        
        return overall_score, category_scores