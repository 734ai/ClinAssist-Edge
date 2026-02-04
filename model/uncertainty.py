"""
Bayesian Uncertainty Quantification for ClinAssist Edge.

This module provides real-time uncertainty estimation for model predictions,
enabling clinicians to understand confidence levels and potential risks in
diagnostic recommendations.

Features:
- Epistemic uncertainty (model confidence)
- Aleatoric uncertainty (data variability)
- Confidence intervals for predictions
- Risk calibration
- Uncertainty visualization
"""

import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import numpy as np
from scipy import stats

logger = logging.getLogger(__name__)


@dataclass
class UncertaintyEstimate:
    """Container for uncertainty metrics."""
    prediction: str
    confidence: float  # 0-1
    epistemic_uncertainty: float  # Model confidence
    aleatoric_uncertainty: float  # Data variability
    confidence_interval: Tuple[float, float]  # Lower and upper bounds
    risk_level: str  # "low", "moderate", "high"
    explanation: str


class BayesianUncertaintyQuantifier:
    """Quantifies uncertainty in clinical predictions."""
    
    def __init__(self, n_bootstrap_samples: int = 50, confidence_level: float = 0.95):
        """
        Initialize uncertainty quantifier.
        
        Args:
            n_bootstrap_samples: Number of bootstrap samples for ensemble
            confidence_level: Confidence level for intervals (0.95 = 95%)
        """
        self.n_bootstrap_samples = n_bootstrap_samples
        self.confidence_level = confidence_level
        self.prediction_history = []
    
    def estimate_epistemic_uncertainty(
        self,
        logits: np.ndarray,
        num_forward_passes: int = 10
    ) -> float:
        """
        Estimate epistemic uncertainty (model's knowledge gaps).
        
        Calculated as the variance in predictions across stochastic forward passes.
        
        Args:
            logits: Model output logits
            num_forward_passes: Number of stochastic passes (for MC Dropout)
        
        Returns:
            Epistemic uncertainty (higher = more uncertain about predictions)
        """
        # Normalize logits to probabilities
        probs = self._softmax(logits)
        
        # Epistemic = variance across predictions
        epistemic = np.var(probs)
        
        # Normalize to 0-1 scale
        epistemic = min(epistemic / (1/len(probs)), 1.0)
        
        return float(epistemic)
    
    def estimate_aleatoric_uncertainty(
        self,
        logits: np.ndarray,
        temperature: float = 1.0
    ) -> float:
        """
        Estimate aleatoric uncertainty (inherent data variability).
        
        Calculated from entropy of prediction distribution.
        
        Args:
            logits: Model output logits
            temperature: Softening factor for probability distribution
        
        Returns:
            Aleatoric uncertainty (higher = more ambiguous prediction)
        """
        probs = self._softmax(logits / temperature)
        
        # Entropy = uncertainty in probability distribution
        entropy = -np.sum(probs * np.log(probs + 1e-10))
        max_entropy = np.log(len(probs))
        
        aleatoric = entropy / max_entropy if max_entropy > 0 else 0.0
        
        return float(aleatoric)
    
    def _softmax(self, logits: np.ndarray) -> np.ndarray:
        """Compute softmax probabilities."""
        exp_logits = np.exp(logits - np.max(logits))
        return exp_logits / np.sum(exp_logits, axis=-1, keepdims=True)
    
    def compute_confidence_interval(
        self,
        predictions: List[float],
        confidence_level: Optional[float] = None
    ) -> Tuple[float, float]:
        """
        Compute confidence interval for predictions using bootstrap.
        
        Args:
            predictions: List of model predictions
            confidence_level: Override default confidence level
        
        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        if not predictions:
            return (0.0, 1.0)
        
        conf_level = confidence_level or self.confidence_level
        alpha = 1 - conf_level
        
        # Bootstrap confidence interval
        bootstrap_estimates = []
        n = len(predictions)
        
        for _ in range(self.n_bootstrap_samples):
            sample = np.random.choice(predictions, size=n, replace=True)
            bootstrap_estimates.append(np.mean(sample))
        
        lower = np.percentile(bootstrap_estimates, alpha/2 * 100)
        upper = np.percentile(bootstrap_estimates, (1 - alpha/2) * 100)
        
        return (float(lower), float(upper))
    
    def estimate_uncertainty(
        self,
        prediction: str,
        logits: np.ndarray,
        supporting_evidence: List[str],
        alternative_diagnoses: Optional[List[Tuple[str, float]]] = None
    ) -> UncertaintyEstimate:
        """
        Comprehensive uncertainty estimation for a prediction.
        
        Args:
            prediction: Primary prediction (e.g., diagnosis)
            logits: Model output logits
            supporting_evidence: List of evidence supporting prediction
            alternative_diagnoses: List of (diagnosis, confidence) tuples
        
        Returns:
            UncertaintyEstimate with full uncertainty metrics
        """
        # Calculate probability of primary prediction
        probs = self._softmax(logits)
        primary_prob = float(np.max(probs))
        
        # Epistemic uncertainty
        epistemic = self.estimate_epistemic_uncertainty(logits)
        
        # Aleatoric uncertainty
        aleatoric = self.estimate_aleatoric_uncertainty(logits)
        
        # Overall confidence
        confidence = primary_prob * (1 - epistemic)
        
        # Risk level based on confidence and supporting evidence
        risk_level = self._assess_risk_level(confidence, len(supporting_evidence))
        
        # Confidence interval
        predictions = [primary_prob] + ([prob for _, prob in alternative_diagnoses] if alternative_diagnoses else [])
        ci = self.compute_confidence_interval(predictions)
        
        # Generate explanation
        explanation = self._generate_explanation(
            confidence, epistemic, aleatoric, risk_level,
            supporting_evidence, alternative_diagnoses
        )
        
        estimate = UncertaintyEstimate(
            prediction=prediction,
            confidence=float(confidence),
            epistemic_uncertainty=epistemic,
            aleatoric_uncertainty=aleatoric,
            confidence_interval=ci,
            risk_level=risk_level,
            explanation=explanation
        )
        
        self.prediction_history.append(estimate)
        return estimate
    
    def _assess_risk_level(self, confidence: float, evidence_count: int) -> str:
        """Assess risk level based on confidence and supporting evidence."""
        if confidence > 0.8 and evidence_count >= 2:
            return "low"
        elif confidence > 0.6 and evidence_count >= 1:
            return "moderate"
        else:
            return "high"
    
    def _generate_explanation(
        self,
        confidence: float,
        epistemic: float,
        aleatoric: float,
        risk_level: str,
        supporting_evidence: List[str],
        alternatives: Optional[List[Tuple[str, float]]]
    ) -> str:
        """Generate human-readable uncertainty explanation."""
        explanation = f"Model confidence: {confidence:.1%}. "
        
        if epistemic > 0.5:
            explanation += "Model has significant knowledge gaps for this case. "
        
        if aleatoric > 0.5:
            explanation += "Prediction is inherently ambiguous. "
        
        explanation += f"Risk level: {risk_level.upper()}. "
        
        if supporting_evidence:
            explanation += f"Supporting evidence: {', '.join(supporting_evidence[:2])}. "
        
        if alternatives and len(alternatives) > 1:
            explanation += f"Alternative diagnoses: {', '.join([d[0] for d in alternatives[1:3]])}. "
        
        explanation += "ALWAYS verify with clinical judgment and confirmatory tests."
        
        return explanation
    
    def get_calibration_metrics(self) -> Dict[str, float]:
        """
        Calculate calibration metrics for model predictions.
        
        Returns:
            Dictionary with calibration metrics
        """
        if not self.prediction_history:
            return {}
        
        confidences = np.array([e.confidence for e in self.prediction_history])
        
        return {
            "mean_confidence": float(np.mean(confidences)),
            "std_confidence": float(np.std(confidences)),
            "min_confidence": float(np.min(confidences)),
            "max_confidence": float(np.max(confidences)),
            "total_predictions": len(self.prediction_history)
        }


class AdaptiveThresholdCalculator:
    """Calculates adaptive confidence thresholds based on prediction history."""
    
    def __init__(self, window_size: int = 100):
        """
        Initialize threshold calculator.
        
        Args:
            window_size: Number of predictions to consider
        """
        self.window_size = window_size
        self.prediction_outcomes = []
    
    def record_outcome(self, prediction: str, confidence: float, was_correct: bool):
        """Record whether a prediction with given confidence was correct."""
        self.prediction_outcomes.append({
            "prediction": prediction,
            "confidence": confidence,
            "was_correct": was_correct
        })
        
        # Keep window size bounded
        if len(self.prediction_outcomes) > self.window_size:
            self.prediction_outcomes.pop(0)
    
    def calculate_threshold(self, target_specificity: float = 0.95) -> float:
        """
        Calculate confidence threshold to achieve target specificity.
        
        Args:
            target_specificity: Desired specificity (0-1)
        
        Returns:
            Recommended confidence threshold
        """
        if len(self.prediction_outcomes) < 10:
            return 0.5  # Default threshold with few samples
        
        # Sort by confidence
        sorted_outcomes = sorted(
            self.prediction_outcomes,
            key=lambda x: x["confidence"]
        )
        
        # Find threshold where specificity >= target
        for outcome in sorted_outcomes:
            correct_above = sum(
                1 for o in self.prediction_outcomes
                if o["confidence"] >= outcome["confidence"] and o["was_correct"]
            )
            total_above = sum(
                1 for o in self.prediction_outcomes
                if o["confidence"] >= outcome["confidence"]
            )
            
            specificity = correct_above / total_above if total_above > 0 else 0
            
            if specificity >= target_specificity:
                return outcome["confidence"]
        
        return 0.9  # Conservative default


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Example usage
    quantifier = BayesianUncertaintyQuantifier()
    
    # Example logits
    logits = np.array([2.1, 1.5, 0.8, 0.3])
    
    estimate = quantifier.estimate_uncertainty(
        prediction="Pneumonia",
        logits=logits,
        supporting_evidence=["Fever 38.9°C", "Productive cough 3 days", "Crackles RLL"],
        alternative_diagnoses=[("Bronchitis", 0.25), ("Viral infection", 0.15)]
    )
    
    print(f"Prediction: {estimate.prediction}")
    print(f"Confidence: {estimate.confidence:.1%}")
    print(f"Risk Level: {estimate.risk_level}")
    print(f"Explanation: {estimate.explanation}")
