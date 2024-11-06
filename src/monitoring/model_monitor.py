import os
import json
import datetime
from typing import Optional, Dict
import logging

class ModelMonitor:
    """Monitor model performance and drift."""
    
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.performance_history = []
        self.drift_threshold = 0.1
        self.calibration_interval = datetime.timedelta(days=7)
        self.last_calibration = datetime.datetime.now()
        
        os.makedirs("monitoring", exist_ok=True)
        
    def track_performance(self, prediction: Dict):
        """Track model performance metrics."""
        metrics = {
            "timestamp": datetime.datetime.now().isoformat(),
            "confidence": prediction.get("verification_result", {}).get("confidence", 0),
            "processing_time": prediction.get("processing_time", 0)
        }
        
        file_path = f"monitoring/{self.model_name}_performance.jsonl"
        with open(file_path, 'a') as f:
            f.write(json.dumps(metrics) + '\n')
            
        self.performance_history.append(metrics)
        
    def detect_drift(self) -> Optional[str]:
        """Detect performance drift."""
        if len(self.performance_history) < 10:
            return None
            
        recent = self.performance_history[-10:]
        avg_confidence = sum(r["confidence"] for r in recent) / 10
        
        if avg_confidence < 50:
            return "Performance degradation detected"
        return None
        
    def check_calibration(self) -> bool:
        """Check if calibration is needed."""
        return (datetime.datetime.now() - self.last_calibration) > self.calibration_interval