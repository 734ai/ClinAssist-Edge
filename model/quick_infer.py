
from transformers import AutoTokenizer, AutoModelForCausalLM, StoppingCriteria, StoppingCriteriaList
import torch
import sys
import os
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the parent directory to sys.path to import load_model
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from load_model import load_model, MODEL_NAME

def read_template(template_name):
    """Read and parse prompt template from templates.md with error handling."""
    try:
        template_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), '..', 'prompts', 'templates.md'
        )
        
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template file not found at {template_path}")
        
        with open(template_path, 'r') as f:
            content = f.read()

        escaped_template_name = re.escape(template_name)
        pattern = re.compile(
            r'#\s*' + escaped_template_name + r'\s*Template\n(.*?)(?=\n#\s*|\Z)', 
            re.DOTALL
        )
        match = pattern.search(content)

        if match:
            template_text = match.group(1).strip()
            logger.info(f"Successfully loaded template: {template_name}")
            return template_text
        else:
            raise ValueError(f"Template '{template_name}' not found in templates.md")
    
    except Exception as e:
        logger.error(f"Error reading template '{template_name}': {str(e)}")
        raise

class StopOnTokens(StoppingCriteria):
    """Define stopping criteria for generation."""
    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs) -> bool:
        return False

def infer(model, tokenizer, template_name, input_data, max_new_tokens=256):
    """
    Perform inference with error handling and validation.
    
    Args:
        model: Loaded language model
        tokenizer: Model tokenizer
        template_name: Name of the prompt template to use
        input_data: Dictionary with input variables for the template
        max_new_tokens: Maximum tokens to generate
        
    Returns:
        Tuple of (full_prompt, generated_output, model_name)
        
    Raises:
        ValueError: If template is not found or input_data is missing required keys
        RuntimeError: If model inference fails
    """
    try:
        # Validate inputs
        if not template_name or not isinstance(template_name, str):
            raise ValueError("template_name must be a non-empty string")
        
        if not input_data or not isinstance(input_data, dict):
            raise ValueError("input_data must be a non-empty dictionary")
        
        # 1. Read the appropriate prompt template
        template = read_template(template_name)

        # 2. Combine input data with template
        try:
            full_prompt = template.format(**input_data)
        except KeyError as e:
            raise ValueError(f"Missing required input key for template {template_name}: {str(e)}")

        # 3. Tokenize input
        inputs = tokenizer(full_prompt, return_tensors="pt").to(model.device)
        
        # Check token count
        token_count = inputs.input_ids.shape[1]
        if token_count > 2048:
            logger.warning(f"Input prompt has {token_count} tokens; may exceed model limits")

        # 4. Generate output with error handling
        try:
            with torch.no_grad():
                out = model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    do_sample=True,
                    temperature=0.7,
                    top_p=0.9,
                    pad_token_id=tokenizer.eos_token_id
                )
        except RuntimeError as e:
            raise RuntimeError(f"Model generation failed: {str(e)}")

        # 5. Decode output
        try:
            decoded_output = tokenizer.decode(
                out[0][inputs.input_ids.shape[1]:], 
                skip_special_tokens=True
            )
        except Exception as e:
            raise RuntimeError(f"Failed to decode model output: {str(e)}")

        logger.info(f"Successfully completed inference for template: {template_name}")
        return full_prompt, decoded_output.strip(), MODEL_NAME
    
    except Exception as e:
        logger.error(f"Inference error for template '{template_name}': {str(e)}")
        raise

if __name__ == "__main__":
    print("--- Testing quick_infer.py with error handling ---")
    try:
        tokenizer, model = load_model()

        # Test Differential Diagnosis
        print("\n--- Testing Differential Diagnosis ---")
        dd_input_data = {
            'patient_symptoms': '45-year-old male, fever 38.9C, productive cough, 3 days. SpO2 95%'
        }
        full_prompt_dd, inference_output_dd, model_name_dd = infer(
            model, tokenizer, 'Differential Diagnosis', dd_input_data, max_new_tokens=300
        )
        print("Input Prompt:\n" + full_prompt_dd)
        print("\nInference Output:\n" + inference_output_dd)
        print("Model Used: " + model_name_dd)

        # Test SOAP Note
        print("\n--- Testing SOAP Note ---")
        soap_input_data = {
            'patient_info': 'Patient: John Doe, 45M. Chief Complaint: Productive cough x 3 days. Vital Signs: Temp 38.9C, SpO2 95%. Lungs: crackles in right lower lobe.'
        }
        full_prompt_soap, inference_output_soap, model_name_soap = infer(
            model, tokenizer, 'SOAP Note', soap_input_data, max_new_tokens=300
        )
        print("Input Prompt:\n" + full_prompt_soap)
        print("\nInference Output:\n" + inference_output_soap)
        print("Model Used: " + model_name_soap)

        # Test Patient Instructions
        print("\n--- Testing Patient Instructions ---")
        pi_input_data = {
            'clinical_output': 'Diagnosis: Community Acquired Pneumonia. Treatment: Azithromycin 500mg daily for 5 days. Advice: Rest, hydration, follow-up in 3 days or if worsening.'
        }
        full_prompt_pi, inference_output_pi, model_name_pi = infer(
            model, tokenizer, 'Patient Instructions', pi_input_data, max_new_tokens=300
        )
        print("Input Prompt:\n" + full_prompt_pi)
        print("\nInference Output:\n" + inference_output_pi)
        print("Model Used: " + model_name_pi)

        print("\nQuick inference test with error handling successful.")

    except Exception as e:
        print("Error during quick inference test: " + str(e))
        print("Make sure the model is downloaded and accessible, and adjust resources if needed.")
        sys.exit(1)
