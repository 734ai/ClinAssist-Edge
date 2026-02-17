#!/usr/bin/env python3
"""
ClinAssist Edge - Interactive Demo Script

This script demonstrates the three core capabilities of ClinAssist Edge:
1. Differential Diagnosis & Red Flags
2. SOAP Note Generation
3. Patient Instructions Translation

Usage:
    python demo/demo_interactive.py

The script will walk through realistic clinical scenarios with clear output.
"""

import sys
import os
import time
from typing import Tuple

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from model.load_model import load_model, MODEL_NAME
from model.quick_infer import infer
from model.safety_checks import perform_safety_check
from utils.logger import log_inference

# Try to import advanced modules
try:
    from model.rag_system import initialize_default_knowledge_base
    from model.uncertainty import BayesianUncertaintyQuantifier
    from model.drug_interactions import DrugInteractionChecker, format_safety_report
    ADVANCED_AVAILABLE = True
except ImportError:
    ADVANCED_AVAILABLE = False


# ANSI color codes for terminal output
class Colors:
    """ANSI color codes for pretty printing."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text: str) -> None:
    """Print a formatted header."""
    print(f"\n{Colors.BOLD}{Colors.OKCYAN}{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}{Colors.ENDC}\n")


def print_section(text: str) -> None:
    """Print a section header."""
    print(f"{Colors.BOLD}{Colors.OKBLUE}→ {text}{Colors.ENDC}")


def print_success(text: str) -> None:
    """Print success message."""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")


def print_warning(text: str) -> None:
    """Print warning message."""
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")


def print_error(text: str) -> None:
    """Print error message."""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")


def slow_print(text: str, delay: float = 0.03) -> None:
    """Print text with typewriter effect."""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()


def run_demo_case(
    model, 
    tokenizer, 
    template_name: str, 
    input_data: dict,
    description: str,
    case_title: str
) -> Tuple[str, str]:
    """Run a single demo case and return the full prompt and output."""
    print_section(f"{case_title}: {description}")
    
    # Display input
    for key, value in input_data.items():
        print(f"  Input ({key}): {value[:100]}..." if len(value) > 100 else f"  Input ({key}): {value}")
    
    print()
    print_section("Processing with MedGemma...")
    
    # Perform inference
    try:
        full_prompt, output, model_used = infer(
            model, tokenizer, template_name, input_data, max_new_tokens=400
        )
        
        print(f"  Model: {model_used}")
        print(f"  Template: {template_name}")
        
        # Perform safety checks
        high_risk_flag, safety_message = perform_safety_check(output)
        
        if high_risk_flag:
            print_warning(f"Safety Check Alert: {safety_message}")
        else:
            print_success("Safety checks passed")
        
        # Log the inference
        log_inference(full_prompt, output, template_name, model_used)
        
        return full_prompt, output
    
    except Exception as e:
        print_error(f"Error during inference: {str(e)}")
        return "", ""


def demo_differential_diagnosis(model, tokenizer) -> None:
    """Demo: Differential Diagnosis & Red Flags."""
    print_header("DEMO 1: DIFFERENTIAL DIAGNOSIS & RED FLAGS")
    
    print(f"""
{Colors.BOLD}Scenario:{Colors.ENDC}
A 60-year-old female presents to a rural clinic with acute respiratory symptoms.
The clinic has limited specialist support and needs AI-assisted diagnosis triage.
    """)
    
    # Case 1: Typical Pneumonia
    case1_input = {
        'patient_symptoms': '''
        60-year-old female
        Chief Complaint: Productive cough x 3 days
        Vital Signs: Temperature 39.5°C, BP 128/82, HR 102, RR 24, SpO2 90%
        History: Acute onset, yellow-green sputum, chest pain on deep breathing
        Lungs: Crackles in right lower lobe
        '''
    }
    
    prompt1, output1 = run_demo_case(
        model, tokenizer, 'Differential Diagnosis', case1_input,
        "Acute respiratory infection with hypoxia",
        "Case 1"
    )
    
    print(f"\n{Colors.BOLD}Generated Output:{Colors.ENDC}")
    print(output1)
    
    # Case 2: Mild URI
    print("\n" + "-"*70 + "\n")
    
    case2_input = {
        'patient_symptoms': '''
        28-year-old male
        Chief Complaint: Cough and sore throat x 2 days
        Vital Signs: Temperature 37.8°C, BP 118/76, HR 78, RR 18, SpO2 98%
        Symptoms: Gradual onset, dry cough, runny nose, mild fatigue
        History: Exposure to ill contacts at workplace
        '''
    }
    
    prompt2, output2 = run_demo_case(
        model, tokenizer, 'Differential Diagnosis', case2_input,
        "Mild URI symptoms with normal vitals",
        "Case 2"
    )
    
    print(f"\n{Colors.BOLD}Generated Output:{Colors.ENDC}")
    print(output2)


def demo_soap_notes(model, tokenizer) -> None:
    """Demo: SOAP Note Generation."""
    print_header("DEMO 2: AUTOMATED SOAP NOTE GENERATION")
    
    print(f"""
{Colors.BOLD}Scenario:{Colors.ENDC}
A clinic nurse sees a post-operative patient and needs to document the encounter.
ClinAssist Edge can generate structured SOAP notes to reduce documentation burden.
    """)
    
    # Case 1: Post-operative Follow-up
    case1_input = {
        'patient_info': '''
        Patient: Maria Garcia, 52-year-old female
        Date: 2026-01-23
        Chief Complaint: Post-operative follow-up, day 5 after appendectomy
        
        Subjective:
        - Reports mild incisional pain (3/10), well-controlled with ibuprofen
        - Denies nausea, vomiting, or fever
        - Tolerating oral intake well, bowel movements normal
        - Ambulating without difficulty
        
        Objective:
        - Vital Signs: BP 128/82, HR 76, Temp 37.0°C, RR 16
        - Abdomen: Surgical site clean, dry, intact. Sutures intact. Mild erythema at edges (expected).
        - No abdominal distension, bowel sounds present in all quadrants
        
        Assessment & Plan:
        - Post-operative day 5, appendectomy, uncomplicated
        - Recommend: Continue current analgesia, suture removal in 1-2 weeks
        '''
    }
    
    prompt1, output1 = run_demo_case(
        model, tokenizer, 'SOAP Note', case1_input,
        "Post-operative recovery follow-up",
        "Case 1"
    )
    
    print(f"\n{Colors.BOLD}Generated SOAP Note:{Colors.ENDC}")
    print(output1)
    
    # Case 2: Chronic Disease Management
    print("\n" + "-"*70 + "\n")
    
    case2_input = {
        'patient_info': '''
        Patient: Robert Johnson, 55-year-old male
        Date: 2026-01-23
        Chief Complaint: Hypertension follow-up, 1 month after initial diagnosis
        
        Subjective:
        - Reports occasional mild headaches, especially in mornings
        - Denies chest pain, shortness of breath, or dizziness
        - Compliant with lisinopril 10mg daily
        - Attempting dietary modifications (reduced salt intake)
        
        Objective:
        - Vital Signs: BP 138/88 (down from 150/95 last visit), HR 72, Temp 37.1°C
        - General: Alert, oriented, no acute distress
        - Cardiovascular: Regular rate and rhythm, no murmurs
        
        Assessment & Plan:
        - Hypertension, improved on current medication
        - Continue lisinopril, add second agent if BP doesn't improve to <130/80
        - Recheck BP in 4 weeks
        '''
    }
    
    prompt2, output2 = run_demo_case(
        model, tokenizer, 'SOAP Note', case2_input,
        "Chronic hypertension management",
        "Case 2"
    )
    
    print(f"\n{Colors.BOLD}Generated SOAP Note:{Colors.ENDC}")
    print(output2)


def demo_patient_instructions(model, tokenizer) -> None:
    """Demo: Patient Instructions Translation."""
    print_header("DEMO 3: PLAIN-LANGUAGE PATIENT INSTRUCTIONS")
    
    print(f"""
{Colors.BOLD}Scenario:{Colors.ENDC}
Clinicians often struggle to explain medical diagnoses and treatment plans in
language that patients can understand. ClinAssist Edge translates clinical jargon
into clear, actionable instructions that improve patient compliance and outcomes.
    """)
    
    # Case 1: Diabetes Diagnosis
    case1_input = {
        'clinical_output': '''
        Diagnosis: Type 2 Diabetes Mellitus (newly diagnosed)
        Labs: FBS 156 mg/dL, HbA1c 7.8%
        Treatment Plan:
        - Metformin 500mg twice daily with meals
        - Lifestyle modification: Weight loss 5-10%, 150 min/week aerobic exercise, low-glycemic diet
        - Self-monitoring: Check blood glucose daily before meals and at bedtime
        - Follow-up: Repeat HbA1c in 3 months, see nutritionist
        Complications to watch: Diabetic ketoacidosis (symptoms: persistent vomiting, rapid breathing)
        '''
    }
    
    prompt1, output1 = run_demo_case(
        model, tokenizer, 'Patient Instructions', case1_input,
        "Newly diagnosed diabetes with medication and lifestyle modifications",
        "Case 1"
    )
    
    print(f"\n{Colors.BOLD}Plain-Language Patient Instructions:{Colors.ENDC}")
    print(output1)
    
    # Case 2: Antibiotic Instructions
    print("\n" + "-"*70 + "\n")
    
    case2_input = {
        'clinical_output': '''
        Diagnosis: Community Acquired Pneumonia (CAP), mild-to-moderate severity
        Causative organism: Likely atypical (viral or bacterial)
        Treatment: Azithromycin 500mg on day 1, then 250mg daily for 4 days
        Supportive Care: Rest, hydration (2-3L/day), acetaminophen 500mg q6h for fever/pain
        Red Flags: Worsening shortness of breath, high fever (>39.5°C), confusion, blood in sputum
        Follow-up: Clinical reassessment in 3-5 days; chest X-ray if not improving
        Duration: If no improvement in 48-72 hours, consider hospitalization
        '''
    }
    
    prompt2, output2 = run_demo_case(
        model, tokenizer, 'Patient Instructions', case2_input,
        "Community acquired pneumonia with antibiotic therapy",
        "Case 2"
    )
    
    print(f"\n{Colors.BOLD}Plain-Language Patient Instructions:{Colors.ENDC}")
    print(output2)


def demo_advanced_features() -> None:
    """Demo: Advanced Features (RAG, Uncertainty, Drug Safety)."""
    if not ADVANCED_AVAILABLE:
        print_warning("Advanced features not available (missing dependencies). Skipping.")
        return

    print_header("DEMO 4: ADVANCED CAPABILITIES (NEW!)")
    
    print(f"""
{Colors.BOLD}Scenario:{Colors.ENDC}
Beyond standard inference, ClinAssist Edge now features state-of-the-art capabilities:
1. RAG: Evidence-backed answers from local medical guidelines
2. Uncertainty: Bayesian confidence estimation
3. Drug Safety: Real-time interaction checking
    """)
    
    # 1. RAG Demo
    print_section("Retrieval-Augmented Generation (RAG)")
    print("Initializing local knowledge base...")
    kb = initialize_default_knowledge_base()
    
    query = "treatment for malaria"
    print(f"Querying knowledge base: '{query}'")
    results = kb.retrieve(query, top_k=1)
    
    if results:
        res = results[0]
        print(f"\n{Colors.OKGREEN}Found Evidence:{Colors.ENDC}")
        print(f"Source: {res.source} (Relevance: {res.relevance_score:.2%})")
        print(f"Content: {res.content}")
    
    # 2. Uncertainty Demo
    print("\n" + "-"*70 + "\n")
    print_section("Bayesian Uncertainty Quantification")
    
    quantifier = BayesianUncertaintyQuantifier()
    # Simulate logits for a high-confidence prediction
    import numpy as np
    logits = np.array([2.5, 0.5, 0.2, 0.1]) 
    
    print("Analyzing prediction confidence...")
    estimate = quantifier.estimate_uncertainty(
        prediction="Pneumonia",
        logits=logits,
        supporting_evidence=["Fever", "Cough"],
        alternative_diagnoses=[("Bronchitis", 0.15)]
    )
    
    print(f"Prediction: {estimate.prediction}")
    print(f"Confidence: {estimate.confidence:.1%}")
    print(f"Risk Level: {estimate.risk_level}")
    print(f"Explanation: {estimate.explanation}")
    
    # 3. Drug Safety Demo
    print("\n" + "-"*70 + "\n")
    print_section("Medication Safety Check")
    
    checker = DrugInteractionChecker()
    meds = ["warfarin", "aspirin"]
    print(f"Checking interactions for: {', '.join(meds)}")
    
    interactions = checker.check_drug_drug_interactions(meds)
    
    for i in interactions:
        print(f"{Colors.FAIL}⚠ {i.severity.value} INTERACTION:{Colors.ENDC} {i.drug1} + {i.drug2}")
        print(f"   Mechanism: {i.mechanism}")
        print(f"   Recommendation: {i.recommendation}")


def main() -> None:
    """Main demo execution."""
    print(f"""
{Colors.BOLD}{Colors.HEADER}
╔══════════════════════════════════════════════════════════════════════════════╗
║                     ClinAssist Edge - Interactive Demo                        ║
║                 Offline AI Co-pilot for Clinical Reasoning                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
{Colors.ENDC}

This demo showcases three core capabilities:
1. 🔍 Differential Diagnosis & Red Flag Detection
2. 📝 Automated SOAP Note Generation
3. 💬 Patient-Friendly Instruction Translation

All inferences are performed locally without external API calls.
    """)
    
    # Load model
    print_section("Loading Model")
    try:
        tokenizer, model = load_model()
        print_success(f"Model loaded: {MODEL_NAME}")
    except Exception as e:
        print_error(f"Failed to load model: {str(e)}")
        print("\nPlease ensure all dependencies are installed:")
        print("  pip install -r requirements.txt")
        sys.exit(1)
    
    try:
        # Run demos
        demo_differential_diagnosis(model, tokenizer)
        demo_soap_notes(model, tokenizer)
        demo_patient_instructions(model, tokenizer)
        demo_advanced_features()
        
        # Closing message
        print_header("DEMO COMPLETE")
        print(f"""
{Colors.OKGREEN}✓ All demonstrations completed successfully!{Colors.ENDC}

Key Takeaways:
  • ClinAssist Edge runs entirely offline - no data leaves your device
  • All outputs are logged for audit and compliance purposes
  • Safety checks flag potentially harmful recommendations
  • Clinician review is mandatory before acting on AI suggestions

Next Steps:
  • Review audit_log.txt to see inference logs
  • Try the interactive Streamlit app: streamlit run app/streamlit_app.py
  • Explore customization options in prompts/templates.md
  • For production deployment, see DEPLOYMENT.md

{Colors.BOLD}Important Disclaimer:{Colors.ENDC}
ClinAssist Edge is a clinical decision support tool, not a replacement for
qualified healthcare professionals. All AI-generated recommendations must be
reviewed and confirmed by licensed clinicians before being acted upon.
        """)
    
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print_error(f"Unexpected error during demo: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
