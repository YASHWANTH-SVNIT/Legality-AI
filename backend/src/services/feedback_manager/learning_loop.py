import logging
from typing import List, Dict
from datetime import datetime

logger = logging.getLogger(__name__)

class LearningLoop:

    def __init__(self, feedback_manager):
        self.feedback_mgr = feedback_manager
    
    def analyze_feedback_patterns(self) -> Dict:
        """
        Analyze patterns in user feedback to identify:
        - Common false positives
        - Common false negatives
        - Categories with low accuracy
        """
        stats = self.feedback_mgr.get_feedback_stats()
        
        patterns = {
            "false_positive_rate": 0.0,
            "false_negative_rate": 0.0,
            "categories_needing_improvement": [],
            "total_feedback": stats.get("total_feedback", 0)
        }
        
        if patterns["total_feedback"] == 0:
            return patterns
        
        by_type = stats.get("by_type", {})
        fp_count = by_type.get("false_positive", 0)
        fn_count = by_type.get("false_negative", 0)
        
        total = patterns["total_feedback"]
        patterns["false_positive_rate"] = (fp_count / total) * 100
        patterns["false_negative_rate"] = (fn_count / total) * 100
        
        # Identify problematic categories
        by_category = stats.get("by_category", {})
        for category, count in by_category.items():
            if count >= 5:  # Threshold: 5+ feedback items
                patterns["categories_needing_improvement"].append(category)
        
        return patterns
    
    def get_improvement_suggestions(self) -> List[str]:
        """
        Generate suggestions for improving the system
        """
        patterns = self.analyze_feedback_patterns()
        suggestions = []
        
        if patterns["false_positive_rate"] > 20:
            suggestions.append(
                f"High false positive rate ({patterns['false_positive_rate']:.1f}%). "
                "Consider raising risk thresholds or improving category detection."
            )
        
        if patterns["false_negative_rate"] > 20:
            suggestions.append(
                f"High false negative rate ({patterns['false_negative_rate']:.1f}%). "
                "Consider lowering risk thresholds or expanding detection patterns."
            )
        
        if patterns["categories_needing_improvement"]:
            cats = ", ".join(patterns["categories_needing_improvement"])
            suggestions.append(
                f"Categories needing attention: {cats}. "
                "Review and update vector DB with approved feedback."
            )
        
        return suggestions
    
    def should_retrain(self) -> bool:
        """
        Decide if system should be retrained based on feedback volume
        """
        stats = self.feedback_mgr.get_feedback_stats()
        
        # Retrain thresholds
        total = stats.get("total_feedback", 0)
        approved_fixes = stats.get("by_type", {}).get("fix_approved", 0)
        
        # Retrain if:
        # - 50+ total feedback items, OR
        # - 20+ approved fixes (high-quality training data)
        return total >= 50 or approved_fixes >= 20
    
    def export_training_data(self) -> str:
        """
        Export approved feedback for retraining vector DB
        """
        export_path = self.feedback_mgr.export_feedback_for_review()
        
        if export_path:
            logger.info(f"✅ Training data exported to {export_path}")
            return export_path
        
        return ""