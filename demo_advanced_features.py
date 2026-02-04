#!/usr/bin/env python3
"""
ClinAssist Edge - Advanced Features Quick Start Demo

This script demonstrates all advanced features in an integrated workflow.
Run this to verify everything is working correctly.
"""

import sys
import os
import logging
from datetime import datetime

# Setup paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def demo_rag_system():
    """Demonstrate RAG system."""
    print("\n" + "="*60)
    print("1. RETRIEVAL-AUGMENTED GENERATION (RAG)")
    print("="*60)
    
    try:
        from model.rag_system import initialize_default_knowledge_base
        
        kb = initialize_default_knowledge_base()
        
        query = "fever and productive cough for 3 days"
        print(f"\nQuery: {query}")
        print("\nRetrieving evidence...")
        
        results = kb.retrieve(query, top_k=3)
        
        for i, result in enumerate(results, 1):
            print(f"\n[{i}] {result.source} ({result.relevance_score:.1%} relevant)")
            print(f"    {result.content[:100]}...")
        
        print("\n✅ RAG system working!")
        return True
    except ImportError as e:
        print(f"⚠️  RAG not available: {e}")
        return False

def demo_uncertainty():
    """Demonstrate uncertainty quantification."""
    print("\n" + "="*60)
    print("2. BAYESIAN UNCERTAINTY QUANTIFICATION")
    print("="*60)
    
    try:
        from model.uncertainty import BayesianUncertaintyQuantifier
        import numpy as np
        
        quantifier = BayesianUncertaintyQuantifier()
        
        logits = np.array([2.1, 1.5, 0.8, 0.3])
        estimate = quantifier.estimate_uncertainty(
            prediction="Pneumonia",
            logits=logits,
            supporting_evidence=["Fever 38.9°C", "Productive cough 3 days", "Crackles RLL"],
            alternative_diagnoses=[("Bronchitis", 0.25), ("Viral infection", 0.15)]
        )
        
        print(f"\nPrediction: {estimate.prediction}")
        print(f"Confidence: {estimate.confidence:.1%}")
        print(f"Epistemic Uncertainty: {estimate.epistemic_uncertainty:.3f}")
        print(f"Aleatoric Uncertainty: {estimate.aleatoric_uncertainty:.3f}")
        print(f"Risk Level: {estimate.risk_level.upper()}")
        print(f"Confidence Interval: {estimate.confidence_interval[0]:.1%} - {estimate.confidence_interval[1]:.1%}")
        print(f"\nExplanation: {estimate.explanation[:200]}...")
        
        print("\n✅ Uncertainty quantification working!")
        return True
    except ImportError as e:
        print(f"⚠️  Uncertainty not available: {e}")
        return False

def demo_explainability():
    """Demonstrate explainability engine."""
    print("\n" + "="*60)
    print("3. EXPLAINABILITY & INTERPRETABILITY")
    print("="*60)
    
    try:
        from model.explainability import ExplainabilityEngine
        
        engine = ExplainabilityEngine()
        
        explanation = engine.explain_decision(
            prediction="Pneumonia",
            confidence=0.87,
            patient_info={"age": 45, "gender": "M"},
            symptoms=["Fever 38.9°C", "Productive cough", "Dyspnea"],
            findings=["Crackles RLL", "SpO2 95%"],
            differential_diagnoses=[("Bronchitis", 0.25), ("Viral infection", 0.12)]
        )
        
        print(f"\nKey Factors (Top 3):")
        for i, factor in enumerate(explanation.key_factors[:3], 1):
            print(f"  {i}. {factor.feature}: {factor.importance_score:.1%}")
        
        print(f"\nReasoning Trace ({len(explanation.reasoning_trace)} steps):")
        for step in explanation.reasoning_trace[:2]:
            print(f"  Step {step.step}: {step.intermediate_conclusion}")
        
        print(f"\nLimitations ({len(explanation.limitations)} noted):")
        for limit in explanation.limitations[:2]:
            print(f"  • {limit}")
        
        print("\n✅ Explainability engine working!")
        return True
    except ImportError as e:
        print(f"⚠️  Explainability not available: {e}")
        return False

def demo_multi_agent():
    """Demonstrate multi-agent reasoning."""
    print("\n" + "="*60)
    print("4. MULTI-AGENT REASONING SYSTEM")
    print("="*60)
    
    try:
        from model.agent_system import AgentOrchestrator
        
        orchestrator = AgentOrchestrator()
        
        patient_context = {
            "age": 45,
            "gender": "M",
            "symptoms": ["fever", "productive cough", "dyspnea"],
            "findings": ["crackles RLL", "SpO2 95%"],
            "allergies": ["Penicillin"],
            "medications": [],
            "contraindications": [],
            "red_flags": []
        }
        
        print("\nRunning multi-agent reasoning chain...")
        results = orchestrator.run_reasoning_chain(
            "45-year-old male with fever and productive cough",
            patient_context
        )
        
        print(f"\nAgent Results:")
        for agent_name, result in results.items():
            print(f"  • {agent_name}: confidence={result['confidence']:.1%}")
        
        print("\n✅ Multi-agent system working!")
        return True
    except ImportError as e:
        print(f"⚠️  Multi-agent not available: {e}")
        return False

def demo_drug_interactions():
    """Demonstrate drug interaction checking."""
    print("\n" + "="*60)
    print("5. DRUG-DISEASE-ALLERGY INTERACTION CHECKER")
    print("="*60)
    
    try:
        from model.drug_interactions import DrugInteractionChecker, InteractionSeverity
        
        checker = DrugInteractionChecker()
        
        safety_check = checker.comprehensive_check(
            medications=["Warfarin", "Aspirin"],
            diseases=["Atrial fibrillation"],
            conditions=[],
            known_allergies=["Penicillin"],
            is_pregnant=False
        )
        
        print(f"\nDrug-Drug Interactions: {len(safety_check['drug_drug_interactions'])}")
        for interaction in safety_check['drug_drug_interactions']:
            print(f"  ⚠️  {interaction.severity.value}: {interaction.drug1} + {interaction.drug2}")
        
        print(f"\nContraindications: {len(safety_check['drug_disease_contraindications'])}")
        for contra in safety_check['drug_disease_contraindications']:
            print(f"  ⚠️  {contra.severity.value}: {contra.drug} in {contra.disease}")
        
        print(f"\nAllergy Checks: {len(safety_check['allergy_checks'])}")
        for med, allergy, severity in safety_check['allergy_checks']:
            print(f"  🚨 {med} may react with {allergy}")
        
        print("\n✅ Drug interaction checker working!")
        return True
    except ImportError as e:
        print(f"⚠️  Drug interaction checker not available: {e}")
        return False

def demo_continuous_learning():
    """Demonstrate continuous learning pipeline."""
    print("\n" + "="*60)
    print("6. CONTINUOUS LEARNING PIPELINE")
    print("="*60)
    
    try:
        from model.continuous_learning import ContinuousLearningPipeline, ClinicalFeedback
        
        pipeline = ContinuousLearningPipeline()
        
        # Record some feedback
        feedback = ClinicalFeedback(
            prediction_id="demo_001",
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
        
        print(f"\nFeedback Recorded:")
        print(f"  Prediction: {feedback.predicted_diagnosis}")
        print(f"  Clinician diagnosis: {feedback.clinician_diagnosis}")
        print(f"  Outcome: {feedback.outcome}")
        
        print(f"\nLearning Pipeline Status:")
        print(f"  Total feedback: {insights['feedback_summary']['total_feedback']}")
        print(f"  Training data size: {insights['training_data_size']}")
        print(f"  Ready for retraining: {insights['ready_for_retraining']}")
        
        print("\n✅ Continuous learning pipeline working!")
        return True
    except ImportError as e:
        print(f"⚠️  Continuous learning not available: {e}")
        return False

def main():
    """Run all demos."""
    print("\n" + "█"*60)
    print("█ ClinAssist Edge - Advanced Features Demo")
    print("█"*60)
    
    results = {
        "RAG System": demo_rag_system(),
        "Uncertainty": demo_uncertainty(),
        "Explainability": demo_explainability(),
        "Multi-Agent": demo_multi_agent(),
        "Drug Interactions": demo_drug_interactions(),
        "Continuous Learning": demo_continuous_learning(),
    }
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    working = sum(1 for v in results.values() if v)
    total = len(results)
    
    for feature, status in results.items():
        status_str = "✅ Working" if status else "⚠️  Not Available"
        print(f"  {feature:<25} {status_str}")
    
    print(f"\nTotal: {working}/{total} features available")
    
    if working == total:
        print("\n🎉 All advanced features are working!")
    elif working > 0:
        print(f"\n⚠️  {total-working} features not available (install missing dependencies)")
    else:
        print("\n❌ Install dependencies: pip install -r requirements-advanced.txt")
    
    print("\n" + "█"*60)
    print("█ To run the enhanced Streamlit app:")
    print("█   streamlit run app/streamlit_app_advanced.py")
    print("█"*60 + "\n")

if __name__ == "__main__":
    main()
