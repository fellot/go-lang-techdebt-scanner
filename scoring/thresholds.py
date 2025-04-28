"""
Threshold Definitions

Defines thresholds for high, medium, and low technical debt.
"""

class DebtThresholds:
    """Defines thresholds for technical debt levels."""
    
    def __init__(self, config):
        """Initialize the debt thresholds.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.thresholds = config['thresholds']
    
    def get_debt_level(self, score):
        """Get the debt level for a score.
        
        Args:
            score: The debt score (0-100)
            
        Returns:
            String: 'low', 'medium', or 'high'
        """
        if score >= self.thresholds['high']:
            return 'high'
        elif score >= self.thresholds['medium']:
            return 'medium'
        else:
            return 'low'
    
    def get_category_thresholds(self, category):
        """Get the thresholds for a specific category.
        
        Args:
            category: The category name
            
        Returns:
            Dictionary with category-specific thresholds
        """
        if category in self.config['category_thresholds']:
            return self.config['category_thresholds'][category]
        else:
            return self.thresholds