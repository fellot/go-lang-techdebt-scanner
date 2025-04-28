"""
Score Normalizer

Normalizes raw metrics to a 0-100 scale where 0 is best (no debt) and 100 is worst.
"""

class ScoreNormalizer:
    """Normalizes raw metrics to a 0-100 scale."""
    
    def normalize(self, value, min_value, max_value):
        """Normalize a value to a 0-100 scale.
        
        Args:
            value: The value to normalize
            min_value: The minimum value (will be normalized to 0)
            max_value: The maximum value (will be normalized to 100)
            
        Returns:
            Normalized value between 0 and 100
        """
        if max_value == min_value:
            return 0
        
        normalized = ((value - min_value) / (max_value - min_value)) * 100
        return max(0, min(100, normalized))
    
    def normalize_inverse(self, value, min_value, max_value):
        """Normalize a value to a 0-100 scale, but inverted (100 - normalized).
        
        Args:
            value: The value to normalize
            min_value: The minimum value (will be normalized to 100)
            max_value: The maximum value (will be normalized to 0)
            
        Returns:
            Normalized value between 0 and 100
        """
        return 100 - self.normalize(value, min_value, max_value)
    
    def normalize_complexity(self, value, ideal, worst):
        """Normalize complexity metrics.
        
        Args:
            value: The complexity value
            ideal: The ideal complexity (will be normalized to 0)
            worst: The worst complexity (will be normalized to 100)
            
        Returns:
            Normalized value between 0 and 100
        """
        return self.normalize(value, ideal, worst)
    
    def normalize_percentage(self, value, ideal, worst):
        """Normalize percentage metrics.
        
        Args:
            value: The percentage value
            ideal: The ideal percentage (will be normalized to 0)
            worst: The worst percentage (will be normalized to 100)
            
        Returns:
            Normalized value between 0 and 100
        """
        return self.normalize(value, ideal, worst)
    
    def normalize_inverse_percentage(self, value, ideal, worst):
        """Normalize percentage metrics where higher is better.
        
        Args:
            value: The percentage value
            ideal: The ideal percentage (will be normalized to 0)
            worst: The worst percentage (will be normalized to 100)
            
        Returns:
            Normalized value between 0 and 100
        """
        return self.normalize_inverse(value, worst, ideal)
    
    def normalize_count(self, value, ideal, worst):
        """Normalize count metrics.
        
        Args:
            value: The count value
            ideal: The ideal count (will be normalized to 0)
            worst: The worst count (will be normalized to 100)
            
        Returns:
            Normalized value between 0 and 100
        """
        return self.normalize(value, ideal, worst)
    
    def normalize_ratio(self, value, ideal, worst):
        """Normalize ratio metrics.
        
        Args:
            value: The ratio value
            ideal: The ideal ratio (will be normalized to 0)
            worst: The worst ratio (will be normalized to 100)
            
        Returns:
            Normalized value between 0 and 100
        """
        # If ideal > worst, we want higher values to be better
        if ideal > worst:
            return self.normalize_inverse(value, worst, ideal)
        else:
            return self.normalize(value, ideal, worst)
    
    def normalize_churn(self, value, ideal, worst):
        """Normalize churn metrics.
        
        Args:
            value: The churn value
            ideal: The ideal churn (will be normalized to 0)
            worst: The worst churn (will be normalized to 100)
            
        Returns:
            Normalized value between 0 and 100
        """
        return self.normalize(value, ideal, worst)