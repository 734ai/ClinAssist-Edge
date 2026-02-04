
import os
import datetime

LOG_FILE = os.path.join(os.path.dirname(__file__), '..', 'audit_log.txt')

def log_inference(input_prompt: str, generated_output: str, template_name: str, model_name: str):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"Timestamp: {timestamp}\n"
    log_entry += f"Model: {model_name}\n"
    log_entry += f"Template: {template_name}\n"
    log_entry += f"Input Prompt:\n{input_prompt}\n"
    log_entry += f"Generated Output:\n{generated_output}\n"
    log_entry += "-" * 50 + "\n\n"

    with open(LOG_FILE, 'a') as f:
        f.write(log_entry)

if __name__ == '__main__':
    # Example usage for testing
    print(f"Logging to: {LOG_FILE}")
    log_inference(
        input_prompt="Patient symptoms: Headache, fever",
        generated_output="Differential Diagnosis: Flu, Strep Throat",
        template_name="Differential Diagnosis",
        model_name="gpt2"
    )
    log_inference(
        input_prompt="Clinical output: High blood pressure",
        generated_output="Patient instructions: Eat healthy, exercise",
        template_name="Patient Instructions",
        model_name="gpt2"
    )
    print("Sample log entries written to audit_log.txt")

