
import streamlit as st
import sys
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    filename="clinassist_errors.log",
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Add necessary paths to sys.path for importing modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'model'))

from model.quick_infer import infer
from model.load_model import load_model, MODEL_NAME
from utils.logger import log_inference
from model.safety_checks import perform_safety_check

# Input validation function
def validate_input(input_text: str, min_length: int = 10, max_length: int = 2000) -> tuple[bool, str]:
    """Validate user input with length checks and sanitization."""
    if not input_text or not input_text.strip():
        return False, "Input cannot be empty."
    
    if len(input_text.strip()) < min_length:
        return False, f"Input must be at least {min_length} characters long."
    
    if len(input_text.strip()) > max_length:
        return False, f"Input exceeds maximum length of {max_length} characters."
    
    return True, "Valid input"

# Load model globally to avoid reloading on each rerun
@st.cache_resource
def get_model():
    """Load model with error handling."""
    try:
        tokenizer, model = load_model()
        return tokenizer, model
    except Exception as e:
        error_msg = f"Failed to load model: {str(e)}"
        logging.error(error_msg)
        st.error(f"❌ Model Loading Error: {error_msg}")
        st.info("Please ensure you have the required dependencies installed and sufficient disk space.")
        st.stop()

# Add a placeholder for a spinner while the model loads
with st.spinner('Loading MedGemma model... This might take a moment.'):
    try:
        tokenizer, model = get_model()
    except Exception as e:
        logging.error(f"Unexpected error during model loading: {str(e)}")
        st.stop()

st.set_page_config(layout="wide", page_title="ClinAssist Edge - Offline AI Co-pilot")

st.title("🩺 ClinAssist Edge")
st.subheader("Offline Clinical Reasoning & Documentation Co-pilot")

st.warning("⚠️ This application is for informational and demonstration purposes ONLY. It is NOT a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of a qualified healthcare provider for any medical concerns.")
st.info("🌐 Running in offline-first mode. All inferences are performed locally on your device with open-weight models, ensuring patient data privacy (no external API calls).")

# --- Input Fields ---
st.header("Patient Information Input")

patient_symptoms_dd = st.text_area(
    "Enter Patient Symptoms for Differential Diagnosis (e.g., '45-year-old male, fever 38.9C, productive cough, 3 days. SpO2 95%'):",
    height=150,
    key="patient_symptoms_dd"
)

patient_info_soap = st.text_area(
    "Enter Patient Information for SOAP Note (e.g., 'Patient: John Doe, 45M. Chief Complaint: Productive cough x 3 days. Vital Signs: Temp 38.9C, SpO2 95%. Lungs: crackles in right lower lobe.'):",
    height=150,
    key="patient_info_soap"
)

clinical_output_pi = st.text_area(
    "Enter Clinical Output for Patient Instructions (e.g., 'Diagnosis: Community Acquired Pneumonia. Treatment: Azithromycin 500mg daily for 5 days. Advice: Rest, hydration, follow-up in 3 days or if worsening.'):",
    height=150,
    key="clinical_output_pi"
)

# --- Inference Buttons and Output Display ---
st.header("Generated Outputs")

if st.button("Generate Differential Diagnosis & Red Flags"):
    is_valid, validation_msg = validate_input(patient_symptoms_dd)
    
    if not is_valid:
        st.error(f"⚠️ Input Validation Error: {validation_msg}")
    else:
        try:
            with st.spinner('Generating differential diagnosis...'):
                dd_input_data = {'patient_symptoms': patient_symptoms_dd}
                full_prompt_dd, dd_output, model_name_dd = infer(
                    model, tokenizer, 'Differential Diagnosis', 
                    dd_input_data, max_new_tokens=500
                )
                st.subheader("Ranked Differential Diagnosis & Red Flags:")
                st.write(dd_output)
                log_inference(full_prompt_dd, dd_output, 'Differential Diagnosis', model_name_dd)

                # Perform safety checks
                high_risk_flag, safety_message = perform_safety_check(dd_output)
                if high_risk_flag:
                    st.error(f"🚨 Safety Alert: {safety_message} Please review this output carefully.")
                else:
                    st.success("✅ Safety checks passed.")
        except Exception as e:
            error_msg = f"Error generating differential diagnosis: {str(e)}"
            logging.error(error_msg)
            st.error(f"❌ {error_msg}")
            st.info("Please try again with different input, or check the logs for more details.")

if st.button("Generate SOAP Note"):
    is_valid, validation_msg = validate_input(patient_info_soap)
    
    if not is_valid:
        st.error(f"⚠️ Input Validation Error: {validation_msg}")
    else:
        try:
            with st.spinner('Generating SOAP note...'):
                soap_input_data = {'patient_info': patient_info_soap}
                full_prompt_soap, soap_output, model_name_soap = infer(
                    model, tokenizer, 'SOAP Note', 
                    soap_input_data, max_new_tokens=500
                )
                st.subheader("SOAP Note:")
                st.write(soap_output)
                log_inference(full_prompt_soap, soap_output, 'SOAP Note', model_name_soap)

                # Perform safety checks
                high_risk_flag, safety_message = perform_safety_check(soap_output)
                if high_risk_flag:
                    st.error(f"🚨 Safety Alert: {safety_message} Please review this output carefully.")
                else:
                    st.success("✅ Safety checks passed.")
        except Exception as e:
            error_msg = f"Error generating SOAP note: {str(e)}"
            logging.error(error_msg)
            st.error(f"❌ {error_msg}")
            st.info("Please try again with different input, or check the logs for more details.")

if st.button("Generate Patient Instructions"):
    is_valid, validation_msg = validate_input(clinical_output_pi)
    
    if not is_valid:
        st.error(f"⚠️ Input Validation Error: {validation_msg}")
    else:
        try:
            with st.spinner('Generating patient instructions...'):
                pi_input_data = {'clinical_output': clinical_output_pi}
                full_prompt_pi, pi_output, model_name_pi = infer(
                    model, tokenizer, 'Patient Instructions', 
                    pi_input_data, max_new_tokens=500
                )
                st.subheader("Plain-Language Patient Instructions:")
                st.write(pi_output)
                log_inference(full_prompt_pi, pi_output, 'Patient Instructions', model_name_pi)

                # Perform safety checks
                high_risk_flag, safety_message = perform_safety_check(pi_output)
                if high_risk_flag:
                    st.error(f"🚨 Safety Alert: {safety_message} Please review this output carefully.")
                else:
                    st.success("✅ Safety checks passed.")
        except Exception as e:
            error_msg = f"Error generating patient instructions: {str(e)}"
            logging.error(error_msg)
            st.error(f"❌ {error_msg}")
            st.info("Please try again with different input, or check the logs for more details.")

# Human-in-the-loop reminder and additional info
st.sidebar.markdown('''
---
### ⚕️ Important Safety Notice
All AI-generated outputs require **thorough review and confirmation** by a qualified clinician before being acted upon. The AI is a co-pilot, not a replacement for human judgment.

### 📊 Application Status
- **Model**: {MODEL_NAME}
- **Offline Mode**: ✅ Enabled
- **Audit Logging**: ✅ Active
- **Safety Checks**: ✅ Active

### 🔒 Privacy
All patient data remains on this device. No external API calls are made.

### 📝 Feedback
If you encounter issues, please:
1. Check `clinassist_errors.log` for error details
2. Review `audit_log.txt` for inference history
3. Ensure inputs meet minimum requirements (10+ characters)
''')
