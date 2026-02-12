"""
Observability & Metrics Layer - Production Monitoring
Tracks quality, hallucinations, and system performance.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path


class ProductionLogger:
    """
    Production-grade logging for AI generation pipeline.
    
    Tracks:
    - Input repo/URL
    - Selected style & tone
    - Prompts used
    - Generated content
    - Quality scores
    - Hallucination corrections
    - User feedback
    """
    
    def __init__(self, log_dir: str = "logs"):
        """Initialize logger."""
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (self.log_dir / "posts").mkdir(exist_ok=True)
        (self.log_dir / "metrics").mkdir(exist_ok=True)
        (self.log_dir / "errors").mkdir(exist_ok=True)
        (self.log_dir / "feedback").mkdir(exist_ok=True)
    
    def log_generation(self, generation_data: Dict[str, Any]) -> str:
        """
        Log a complete generation event.
        
        Returns: log_file_path
        """
        timestamp = datetime.now()
        log_entry = {
            "timestamp": timestamp.isoformat(),
            "session_id": generation_data.get("session_id", "unknown"),
            "input": {
                "source": generation_data.get("input_source", "text"),
                "url": generation_data.get("github_url", None),
                "content_length": len(generation_data.get("input_text", "")),
                "hash": hash(generation_data.get("input_text", "")) % 10000
            },
            "configuration": {
                "style": generation_data.get("style", "unknown"),
                "tone": generation_data.get("tone", "unknown"),
                "include_hashtags": generation_data.get("include_hashtags", False),
                "include_caption": generation_data.get("include_caption", False)
            },
            "prompts": {
                "base_prompt": generation_data.get("base_prompt", "")[:200],  # First 200 chars
                "style_prompt": generation_data.get("style_prompt", "")[:200],
                "hashtag_prompt": generation_data.get("hashtag_prompt", "")[:200]
            },
            "output": {
                "post": generation_data.get("post", ""),
                "hashtags": generation_data.get("hashtags", ""),
                "caption": generation_data.get("caption", ""),
                "quality_score": generation_data.get("quality_score", 0)
            },
            "safety": {
                "hallucination_corrections": generation_data.get("hallucination_corrections", 0),
                "policy_violations": generation_data.get("policy_violations", []),
                "safety_confidence": generation_data.get("safety_confidence", 0.0)
            },
            "performance": {
                "total_time": generation_data.get("generation_time", 0),
                "llm_calls": generation_data.get("llm_calls", 0),
                "llm_model": generation_data.get("llm_model", "unknown")
            }
        }
        
        # Save to dated file
        date_str = timestamp.strftime("%Y-%m-%d")
        log_file = self.log_dir / "posts" / f"generations_{date_str}.jsonl"
        
        with open(log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
        
        return str(log_file)
    
    def log_error(self, error_data: Dict[str, Any]) -> str:
        """Log generation errors for debugging."""
        timestamp = datetime.now()
        error_entry = {
            "timestamp": timestamp.isoformat(),
            "error_type": error_data.get("error_type", "unknown"),
            "message": str(error_data.get("message", "")),
            "stage": error_data.get("stage", "unknown"),
            "context": error_data.get("context", {}),
            "traceback": error_data.get("traceback", "")
        }
        
        date_str = timestamp.strftime("%Y-%m-%d")
        error_file = self.log_dir / "errors" / f"errors_{date_str}.jsonl"
        
        with open(error_file, "a") as f:
            f.write(json.dumps(error_entry) + "\n")
        
        return str(error_file)
    
    def log_feedback(self, feedback_data: Dict[str, Any]) -> str:
        """Log user feedback for model improvement."""
        timestamp = datetime.now()
        feedback_entry = {
            "timestamp": timestamp.isoformat(),
            "session_id": feedback_data.get("session_id", "unknown"),
            "post_id": feedback_data.get("post_id", "unknown"),
            "feedback_type": feedback_data.get("type", "unknown"),  # "engaging", "generic", "technical"
            "rating": feedback_data.get("rating", 0),  # 1-5
            "comment": feedback_data.get("comment", ""),
            "would_regenerate": feedback_data.get("would_regenerate", False)
        }
        
        date_str = timestamp.strftime("%Y-%m-%d")
        feedback_file = self.log_dir / "feedback" / f"feedback_{date_str}.jsonl"
        
        with open(feedback_file, "a") as f:
            f.write(json.dumps(feedback_entry) + "\n")
        
        return str(feedback_file)


class QualityMetricsTracker:
    """
    Track quality drift over time.
    
    Metrics:
    - Average quality score (trend)
    - Hallucination correction rate
    - User regeneration rate
    - Policy violation rate
    """
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.metrics_file = self.log_dir / "metrics" / "quality_metrics.json"
        self.log_dir.mkdir(exist_ok=True)
        (self.log_dir / "metrics").mkdir(exist_ok=True)
        
        self.metrics = self._load_metrics()
    
    def _load_metrics(self) -> Dict[str, Any]:
        """Load existing metrics or create new."""
        if self.metrics_file.exists():
            with open(self.metrics_file, "r") as f:
                return json.load(f)
        
        return {
            "total_generations": 0,
            "total_corrections": 0,
            "total_policy_violations": 0,
            "total_regenerations": 0,
            "quality_scores": [],
            "safety_confidence": [],
            "daily_stats": {},
            "last_updated": datetime.now().isoformat()
        }
    
    def record_generation(self, quality_score: float, corrections: int, 
                         policy_violations: int, safety_conf: float):
        """Record metrics from a generation."""
        self.metrics["total_generations"] += 1
        self.metrics["total_corrections"] += corrections
        self.metrics["total_policy_violations"] += len(policy_violations) if isinstance(policy_violations, list) else policy_violations
        self.metrics["quality_scores"].append(quality_score)
        self.metrics["safety_confidence"].append(safety_conf)
        
        # Daily stats
        today = datetime.now().strftime("%Y-%m-%d")
        if today not in self.metrics["daily_stats"]:
            self.metrics["daily_stats"][today] = {
                "count": 0,
                "avg_quality": 0,
                "corrections": 0,
                "violations": 0
            }
        
        daily = self.metrics["daily_stats"][today]
        daily["count"] += 1
        daily["avg_quality"] = sum(self.metrics["quality_scores"][-daily["count"]:]) / daily["count"]
        daily["corrections"] += corrections
        daily["violations"] += len(policy_violations) if isinstance(policy_violations, list) else policy_violations
        
        self.metrics["last_updated"] = datetime.now().isoformat()
        self._save_metrics()
    
    def record_feedback(self, feedback_type: str):
        """Record user feedback (regeneration request)."""
        if feedback_type == "regenerate":
            self.metrics["total_regenerations"] += 1
        self._save_metrics()
    
    def _save_metrics(self):
        """Save metrics to file."""
        with open(self.metrics_file, "w") as f:
            json.dump(self.metrics, f, indent=2)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get quality summary statistics."""
        if not self.metrics["quality_scores"]:
            return {"status": "No data yet"}
        
        quality_scores = self.metrics["quality_scores"]
        safety_conf = self.metrics["safety_confidence"]
        
        return {
            "total_generations": self.metrics["total_generations"],
            "average_quality_score": sum(quality_scores) / len(quality_scores),
            "quality_trend": self._calculate_trend(quality_scores),
            "hallucination_rate": (
                self.metrics["total_corrections"] / self.metrics["total_generations"]
                if self.metrics["total_generations"] > 0 else 0
            ),
            "policy_violation_rate": (
                self.metrics["total_policy_violations"] / self.metrics["total_generations"]
                if self.metrics["total_generations"] > 0 else 0
            ),
            "regeneration_rate": (
                self.metrics["total_regenerations"] / self.metrics["total_generations"]
                if self.metrics["total_generations"] > 0 else 0
            ),
            "average_safety_confidence": sum(safety_conf) / len(safety_conf) if safety_conf else 0,
            "today_stats": self.metrics["daily_stats"].get(
                datetime.now().strftime("%Y-%m-%d"),
                {"count": 0, "avg_quality": 0}
            )
        }
    
    @staticmethod
    def _calculate_trend(scores: List[float]) -> str:
        """Calculate if quality is trending up, down, or stable."""
        if len(scores) < 2:
            return "insufficient_data"
        
        recent = scores[-10:]  # Last 10
        previous = scores[-20:-10] if len(scores) >= 20 else scores[:len(scores)//2]
        
        if not previous:
            return "insufficient_data"
        
        recent_avg = sum(recent) / len(recent)
        previous_avg = sum(previous) / len(previous)
        
        diff = recent_avg - previous_avg
        if diff > 0.05:
            return "↗️ Improving"
        elif diff < -0.05:
            return "↘️ Declining"
        else:
            return "→ Stable"


# Global instances
_logger = None
_metrics_tracker = None


def get_logger() -> ProductionLogger:
    """Get or create logger instance."""
    global _logger
    if _logger is None:
        _logger = ProductionLogger()
    return _logger


def get_metrics_tracker() -> QualityMetricsTracker:
    """Get or create metrics tracker instance."""
    global _metrics_tracker
    if _metrics_tracker is None:
        _metrics_tracker = QualityMetricsTracker()
    return _metrics_tracker
