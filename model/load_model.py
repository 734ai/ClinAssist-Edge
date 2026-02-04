
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import torch
import logging
import os
from huggingface_hub import login

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure HuggingFace authentication
def setup_huggingface_auth():
    """Authenticate with HuggingFace Hub using API key from file or environment."""
    hf_key_file = os.path.join(os.path.dirname(__file__), '..', 'huggingface-api-key')
    
    if os.path.exists(hf_key_file):
        try:
            with open(hf_key_file, 'r') as f:
                token = f.read().strip()
            if token:
                login(token=token, add_to_git_credential=False)
                logger.info("✓ HuggingFace authentication successful")
                return True
        except Exception as e:
            logger.warning(f"Could not read HuggingFace token file: {str(e)}")
    
    # Try environment variable as fallback
    if os.getenv('HF_TOKEN'):
        login(token=os.getenv('HF_TOKEN'), add_to_git_credential=False)
        logger.info("✓ HuggingFace authenticated via HF_TOKEN environment variable")
        return True
    
    logger.warning("⚠ No HuggingFace authentication found. Using public models only.")
    return False

# Authenticate immediately on module load
setup_huggingface_auth()

# Production: Use MedGemma-2B for medical domain knowledge
# Development: Fall back to gpt2 if MedGemma access denied
MODEL_NAME = "google/medgemma-2b"
FALLBACK_MODEL = "gpt2"

def get_device():
    """Detect and return the best available device."""
    if torch.cuda.is_available():
        device = "cuda"
        logger.info(f"CUDA available. Using GPU: {torch.cuda.get_device_name(0)}")
    elif torch.backends.mps.is_available():
        device = "mps"
        logger.info("MPS (Apple Silicon) available. Using GPU acceleration.")
    else:
        device = "cpu"
        logger.info("No GPU detected. Using CPU (inference will be slower).")
    
    return device

def load_model(model_name: str = MODEL_NAME, device: str = "auto", quantize: bool = False):
    """
    Load model with optional quantization for resource-constrained environments.
    
    Args:
        model_name: HuggingFace model identifier
        device: Device to load model on ("auto", "cuda", "cpu", "mps")
        quantize: If True, use 4-bit quantization (requires bitsandbytes)
        
    Returns:
        Tuple of (tokenizer, model)
        
    Raises:
        ValueError: If model cannot be loaded
        RuntimeError: If device setup fails
    """
    try:
        logger.info(f"Attempting to load model: {model_name}")
        
        # Set up device
        if device == "auto":
            device = get_device()
        
        # Load tokenizer
        try:
            tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
            logger.info(f"✓ Tokenizer loaded successfully")
        except Exception as e:
            logger.warning(f"Could not load {model_name}: {str(e)}")
            logger.info(f"Falling back to {FALLBACK_MODEL}")
            model_name = FALLBACK_MODEL
            tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        # Set pad token if not set
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
            logger.info("Pad token set to EOS token")
        
        # Load model with optional quantization
        model_kwargs = {
            "torch_dtype": torch.float16 if torch.cuda.is_available() else torch.float32,
            "device_map": "auto" if device == "cuda" else device,
            "trust_remote_code": True
        }
        
        if quantize:
            try:
                logger.info("Loading model with 4-bit quantization...")
                quantization_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4"
                )
                model_kwargs["quantization_config"] = quantization_config
                logger.info("✓ 4-bit quantization enabled")
            except Exception as e:
                logger.warning(f"Quantization not available: {str(e)}. Loading without quantization.")
                quantize = False
        
        # Load model
        try:
            model = AutoModelForCausalLM.from_pretrained(model_name, **model_kwargs)
            logger.info(f"✓ Model loaded successfully on device: {device}")
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            raise ValueError(f"Could not load model {model_name}: {str(e)}")
        
        # Set evaluation mode
        model.eval()
        
        # Log model info
        total_params = sum(p.numel() for p in model.parameters())
        trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
        logger.info(f"Model parameters - Total: {total_params:,}, Trainable: {trainable_params:,}")
        logger.info(f"Using model: {model_name}")
        
        return tokenizer, model
    
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        raise

if __name__ == "__main__":
    print("--- Testing load_model.py with MedGemma and HuggingFace Auth ---")
    try:
        # Test 1: Standard loading
        print("\n--- Test 1: Standard Loading ---")
        tok, mdl = load_model()
        print(f"✓ Model loaded: {mdl.__class__.__name__}, Tokenizer: {tok.__class__.__name__}")
        
        # Test 2: With quantization (optional)
        print("\n--- Test 2: With Quantization (if available) ---")
        try:
            tok_q, mdl_q = load_model(quantize=True)
            print(f"✓ Quantized model loaded successfully")
        except Exception as e:
            print(f"⚠ Quantization test skipped: {str(e)}")
        
        print("\n✓ Load model test successful.")
        
    except Exception as e:
        print(f"❌ Error loading model: {str(e)}")
        print("Please ensure you have access to the model on Hugging Face Hub and sufficient resources.")
        import sys
        sys.exit(1)
