
import os
import torch
import sys
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer, DataCollatorForLanguageModeling
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from datasets import load_dataset

# Add the parent directory to sys.path to import load_model
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from load_model import load_model, MODEL_NAME

# Constants
LORA_R = 8
LORA_ALPHA = 16
LORA_DROPOUT = 0.05
TARGET_MODULES = ["q_proj", "v_proj"]

def run_lora_finetuning(base_model_id: str, dataset_path: str, output_dir: str, num_train_epochs: int = 1):
    print("\n--- Starting LoRA Fine-tuning for " + base_model_id + " ---")
    print("Dataset: " + dataset_path + ", Output Directory: " + output_dir)

    # 1. Load base model and tokenizer
    print("Loading base model and tokenizer...")
    tokenizer, model = load_model(device="cpu") # Force CPU for fine-tuning setup demonstration

    # Ensure pad_token is set for causal language modeling
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
        model.config.pad_token_id = tokenizer.eos_token_id

    # 2. Prepare model for k-bit training (important for quantized models or memory efficiency)
    # model = prepare_model_for_kbit_training(model) # Uncomment if using quantization

    # 3. Configure LoRA
    lora_config = LoraConfig(
        r=LORA_R,
        lora_alpha=LORA_ALPHA,
        lora_dropout=LORA_DROPOUT,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=TARGET_MODULES,
    )

    # 4. Get PEFT model (LoRA-enabled model)
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    # 5. Load and preprocess dataset
    print("Loading dataset from " + dataset_path + "...")
    dataset = load_dataset('json', data_files=dataset_path, split='train')

    def tokenize_function(examples):
        # Combine instruction, input, and output for instruction tuning
        # Add a separator to distinguish parts (e.g., newline)
        text = ["### Instruction:\n"+instruction+"\n### Input:\n"+input+"\n### Output:\n"+output+"\n"                 for instruction, input, output in zip(examples["instruction"], examples["input"], examples["output"])]
        return tokenizer(text, truncation=True)

    tokenized_dataset = dataset.map(tokenize_function, batched=True, remove_columns=["instruction", "input", "output"])
    print("Dataset tokenized.")

    # 6. Set up TrainingArguments
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=num_train_epochs,
        per_device_train_batch_size=1, # Small batch size for demonstration
        gradient_accumulation_steps=1, # Accumulate gradients for effective larger batch size
        learning_rate=2e-4,
        logging_dir=output_dir + "/logs",
        logging_strategy="epoch",
        save_strategy="no", # Don't save checkpoints during this demo
        report_to="none",
        # Optional: Add fp16=True or bf16=True if your GPU supports it for faster training
    )

    # 7. Initialize Trainer
    data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
        data_collator=data_collator,
    )

    # 8. Start training
    print("Starting training...")
    trainer.train()
    print("Training complete.")

    # 9. Save fine-tuned LoRA adapters
    lora_adapter_path = os.path.join(output_dir, "lora_adapters")
    model.save_pretrained(lora_adapter_path)
    print("LoRA adapters saved to: " + lora_adapter_path)

    print("--- LoRA Fine-tuning Finished ---")

if __name__ == '__main__':
    # Test fine-tuning with a dummy dataset (synthetic_data.jsonl created earlier)
    # Note: Training gpt2 even on a small dataset might take a while on CPU.
    # For a real scenario, use a GPU and potentially more data.
    print("\n--- Testing lora_finetune.py ---")

    dummy_dataset_path = os.path.join(os.getcwd(), 'synthetic_data.jsonl')
    dummy_output_dir = os.path.join(os.getcwd(), 'lora_fine_tuned_model')
    os.makedirs(dummy_output_dir, exist_ok=True)

    try:
        run_lora_finetuning(base_model_id=MODEL_NAME, # Uses the placeholder model (gpt2)
                            dataset_path=dummy_dataset_path,
                            output_dir=dummy_output_dir,
                            num_train_epochs=1) # Small number of epochs for quick demo
        print("LoRA fine-tuning test successful. Adapters should be in 'lora_fine_tuned_model/lora_adapters'.")
    except Exception as e:
        print("Error during LoRA fine-tuning test: " + str(e))
        print("Ensure all dependencies are installed, and consider using a GPU for faster training.")
