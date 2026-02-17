"""
Continuous Learning Pipeline for ClinAssist Edge.

This module implements feedback loops and incremental fine-tuning to improve
the model based on clinician feedback and real-world outcomes.

Features:
- Clinician feedback collection
- Outcome tracking
- Incremental model refinement
- Drift detection
- Performance monitoring
"""

import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import json
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class ClinicalFeedback:
    """Clinical feedback on a prediction."""
    prediction_id: str
    predicted_diagnosis: str
    clinician_diagnosis: str
    confidence: float
    timestamp: datetime
    outcome: str  # "correct", "incorrect", "unclear"
    reasoning: str
    patient_id: str  # For aggregation (anonymized)


@dataclass
class PerformanceMetric:
    """Performance metric for model evaluation."""
    metric_name: str
    value: float
    timestamp: datetime
    sample_size: int


class FeedbackCollector:
    """Collects and stores clinician feedback."""
    
    def __init__(self, db_path: str = "clinician_feedback.db"):
        """
        Initialize feedback collector.
        
        Args:
            db_path: Path to SQLite database for feedback storage
        """
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize feedback database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    prediction_id TEXT PRIMARY KEY,
                    predicted_diagnosis TEXT,
                    clinician_diagnosis TEXT,
                    confidence REAL,
                    timestamp TEXT,
                    outcome TEXT,
                    reasoning TEXT,
                    patient_id TEXT
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY,
                    metric_name TEXT,
                    value REAL,
                    timestamp TEXT,
                    sample_size INTEGER
                )
            """)
            
            conn.commit()
            conn.close()
            logger.info(f"Initialized feedback database: {self.db_path}")
        
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
    
    def record_feedback(self, feedback: ClinicalFeedback):
        """
        Record clinician feedback on a prediction.
        
        Args:
            feedback: ClinicalFeedback object
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO feedback VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                feedback.prediction_id,
                feedback.predicted_diagnosis,
                feedback.clinician_diagnosis,
                feedback.confidence,
                feedback.timestamp.isoformat(),
                feedback.outcome,
                feedback.reasoning,
                feedback.patient_id
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Recorded feedback for prediction {feedback.prediction_id}")
        
        except Exception as e:
            logger.error(f"Failed to record feedback: {e}")
    
    def get_feedback_summary(self) -> Dict:
        """Get summary of collected feedback."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM feedback")
            total_feedback = cursor.fetchone()[0]
            
            cursor.execute("SELECT outcome, COUNT(*) FROM feedback GROUP BY outcome")
            outcomes = dict(cursor.fetchall())
            
            cursor.execute("""
                SELECT predicted_diagnosis, clinician_diagnosis, COUNT(*)
                FROM feedback
                WHERE outcome = 'incorrect'
                GROUP BY predicted_diagnosis, clinician_diagnosis
            """)
            disagreements = cursor.fetchall()
            
            conn.close()
            
            return {
                "total_feedback": total_feedback,
                "outcomes": outcomes,
                "top_disagreements": disagreements[:5]
            }
        
        except Exception as e:
            logger.error(f"Failed to get feedback summary: {e}")
            return {}


class OutcomeTracker:
    """Tracks clinical outcomes for predictions."""
    
    def __init__(self, db_path: str = "clinical_outcomes.db"):
        """
        Initialize outcome tracker.
        
        Args:
            db_path: Path to SQLite database for outcomes
        """
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize outcomes database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS outcomes (
                    prediction_id TEXT PRIMARY KEY,
                    patient_outcome TEXT,  -- "recovered", "hospitalized", "deceased", "unknown"
                    final_diagnosis TEXT,
                    treatment_response TEXT,
                    timestamp TEXT,
                    follow_up_notes TEXT
                )
            """)
            
            conn.commit()
            conn.close()
            logger.info(f"Initialized outcomes database: {self.db_path}")
        
        except Exception as e:
            logger.error(f"Failed to initialize outcomes database: {e}")
    
    def record_outcome(
        self,
        prediction_id: str,
        patient_outcome: str,
        final_diagnosis: str,
        treatment_response: str,
        follow_up_notes: str = ""
    ):
        """
        Record patient outcome following a prediction.
        
        Args:
            prediction_id: ID of original prediction
            patient_outcome: Final patient outcome
            final_diagnosis: Confirmed diagnosis
            treatment_response: How patient responded to treatment
            follow_up_notes: Additional follow-up notes
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO outcomes VALUES (?, ?, ?, ?, ?, ?)
            """, (
                prediction_id,
                patient_outcome,
                final_diagnosis,
                treatment_response,
                datetime.now().isoformat(),
                follow_up_notes
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Recorded outcome for prediction {prediction_id}")
        
        except Exception as e:
            logger.error(f"Failed to record outcome: {e}")
    
    def calculate_prediction_accuracy(self) -> Dict:
        """Calculate accuracy of predictions based on outcomes."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Match predictions with outcomes
            cursor.execute("""
                SELECT COUNT(*) FROM outcomes
            """)
            total = cursor.fetchone()[0]
            
            if total == 0:
                return {"accuracy": 0.0, "sample_size": 0}
            
            # This would compare final_diagnosis with original prediction
            # For now, return structure
            
            conn.close()
            
            return {"accuracy": 0.0, "sample_size": total}
        
        except Exception as e:
            logger.error(f"Failed to calculate accuracy: {e}")
            return {}


class IncrementalFineTuner:
    """Manages incremental model fine-tuning based on feedback."""
    
    def __init__(self, model_name: str = "google/medgemma-2b"):
        """
        Initialize fine-tuner.
        
        Args:
            model_name: Base model identifier
        """
        self.model_name = model_name
        self.training_data = []
        self.training_history = []
    
    def add_training_example(
        self,
        input_text: str,
        target_output: str,
        source: str = "clinician_feedback"
    ):
        """
        Add a training example from feedback or outcomes.
        
        Args:
            input_text: Input prompt
            target_output: Correct output
            source: Source of training example
        """
        example = {
            "input": input_text,
            "output": target_output,
            "source": source,
            "timestamp": datetime.now().isoformat()
        }
        self.training_data.append(example)
        logger.debug(f"Added training example from {source}")
    
    def prepare_training_dataset(self) -> List[Dict]:
        """
        Prepare dataset for fine-tuning.
        
        Returns:
            List of training examples in format suitable for PEFT
        """
        if not self.training_data:
            logger.warning("No training data available")
            return []
        
        # Deduplicate by input
        unique_inputs = {}
        for example in self.training_data:
            if example["input"] not in unique_inputs:
                unique_inputs[example["input"]] = example
        
        logger.info(f"Prepared {len(unique_inputs)} unique training examples")
        return list(unique_inputs.values())
    
    def save_training_data(self, path: str):
        """Save training data for fine-tuning."""
        try:
            with open(path, 'w') as f:
                json.dump(self.training_data, f, indent=2)
            logger.info(f"Saved training data to {path}")
        except Exception as e:
            logger.error(f"Failed to save training data: {e}")


class DriftDetector:
    """Detects model performance degradation."""
    
    def __init__(self, threshold: float = 0.1):
        """
        Initialize drift detector.
        
        Args:
            threshold: Performance drop threshold for alert
        """
        self.threshold = threshold
        self.baseline_metrics = {}
        self.current_metrics = {}
    
    def set_baseline(self, metrics: Dict[str, float]):
        """Set baseline performance metrics."""
        self.baseline_metrics = metrics
        logger.info("Baseline metrics set")
    
    def check_drift(self, new_metrics: Dict[str, float]) -> Tuple[bool, str]:
        """
        Check if performance has degraded significantly.
        
        Args:
            new_metrics: Current performance metrics
        
        Returns:
            Tuple of (drift_detected, explanation)
        """
        if not self.baseline_metrics:
            logger.warning("No baseline metrics set")
            return False, "No baseline available"
        
        drifts = []
        
        for metric, baseline_value in self.baseline_metrics.items():
            if metric not in new_metrics:
                continue
            
            current_value = new_metrics[metric]
            
            # Calculate relative change
            if baseline_value > 0:
                relative_change = abs(current_value - baseline_value) / baseline_value
                
                if relative_change > self.threshold:
                    drifts.append(
                        f"{metric}: {baseline_value:.3f} → {current_value:.3f} "
                        f"({relative_change:.1%} change)"
                    )
        
        if drifts:
            explanation = "Performance drift detected:\n" + "\n".join(drifts)
            logger.warning(explanation)
            return True, explanation
        
        return False, "No significant drift detected"


class ContinuousLearningPipeline:
    """Main pipeline for continuous learning."""
    
    def __init__(self, base_model: str = "google/medgemma-2b"):
        """
        Initialize continuous learning pipeline.
        
        Args:
            base_model: Base model identifier
        """
        self.feedback_collector = FeedbackCollector()
        self.outcome_tracker = OutcomeTracker()
        self.fine_tuner = IncrementalFineTuner(base_model)
        self.drift_detector = DriftDetector()
        
        logger.info("Initialized continuous learning pipeline")
    
    def process_feedback(self, feedback: ClinicalFeedback):
        """
        Process clinician feedback and update learning pipeline.
        
        Args:
            feedback: ClinicalFeedback from clinician
        """
        # Record feedback
        self.feedback_collector.record_feedback(feedback)
        
        # If incorrect, add to training data
        if feedback.outcome == "incorrect":
            self.fine_tuner.add_training_example(
                input_text=f"Diagnosis task: {feedback.predicted_diagnosis}",
                target_output=feedback.clinician_diagnosis,
                source="clinician_correction"
            )
            logger.info(f"Added correction example: {feedback.predicted_diagnosis} → {feedback.clinician_diagnosis}")
    
    def get_learning_insights(self) -> Dict:
        """Get insights from collected feedback and outcomes."""
        feedback_summary = self.feedback_collector.get_feedback_summary()
        
        insights = {
            "feedback_summary": feedback_summary,
            "training_data_size": len(self.fine_tuner.training_data),
            "ready_for_retraining": len(self.fine_tuner.training_data) > 10,
        }
        
        return insights
    
    def export_for_finetuning(self, output_path: str):
        """Export collected data for model fine-tuning."""
        self.fine_tuner.save_training_data(output_path)
        logger.info(f"Exported fine-tuning data to {output_path}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    pipeline = ContinuousLearningPipeline()
    
    # Example feedback
    feedback = ClinicalFeedback(
        prediction_id="pred_001",
        predicted_diagnosis="Pneumonia",
        clinician_diagnosis="Bronchitis",
        confidence=0.85,
        timestamp=datetime.now(),
        outcome="incorrect",
        reasoning="Patient improved without antibiotics",
        patient_id="anon_001"
    )
    
    pipeline.process_feedback(feedback)
    
    insights = pipeline.get_learning_insights()
    print(f"Learning insights: {insights}")
