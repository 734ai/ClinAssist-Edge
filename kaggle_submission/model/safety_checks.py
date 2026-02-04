
import re
from typing import Tuple

def perform_safety_check(generated_output: str) -> Tuple[bool, str]:
    '''Performs rule-based safety checks on the generated output.'''
    high_risk_flag = False
    warning_message = ""

    # Rule 1: Check for explicit medication dosage instructions
    medication_dosage_patterns = [
        r'(\w+ \d+(?:mg|mcg|g|ml) \w+ \d+(?:times|x) \w+)',
        r'take \w+ \d+(?:mg|mcg|g|ml)',
        r'prescribe \w+ \d+(?:mg|mcg|g|ml)'
    ]
    for pattern in medication_dosage_patterns:
        if re.search(pattern, generated_output, re.IGNORECASE):
            high_risk_flag = True
            warning_message += "Potential high-risk: Explicit medication dosage instruction detected. "
            break

    # Rule 2: Check for unqualified diagnoses
    unqualified_diagnosis_patterns = [
        r'the diagnosis is', r'patient has \w+', r'it is certain that \w+'
    ]
    for pattern in unqualified_diagnosis_patterns:
        if re.search(pattern, generated_output, re.IGNORECASE):
            high_risk_flag = True
            warning_message += "Potential high-risk: Unqualified or definitive diagnosis by AI detected. "
            break

    # Rule 3: Check for direct medical advice
    direct_advice_patterns = [
        r'you should \w+', r'i recommend you \w+', r'do \w+ immediately'
    ]
    for pattern in direct_advice_patterns:
        if re.search(pattern, generated_output, re.IGNORECASE):
            high_risk_flag = True
            warning_message += "Potential high-risk: Direct medical advice detected. "
            break

    if high_risk_flag and not warning_message:
        warning_message = "Potential high-risk content detected. Review carefully. "

    return high_risk_flag, warning_message.strip()

if __name__ == '__main__':
    print("--- Testing safety_checks.py ---")

    test_cases = [
        ("The patient should take Amoxicillin 500mg daily for 7 days.", True),
        ("It is certain that the patient has pneumonia.", True),
        ("You should go to the emergency room immediately.", True),
        ("Rest and hydration are recommended. Follow-up with your doctor.", False),
        ("Differential Diagnosis: Bronchitis, Pneumonia, Asthma.", False)
    ]

    for output, expected_flag in test_cases:
        flag, msg = perform_safety_check(output)
        # Corrected print statement to use standard quotes and proper escaping
        print("\nOutput: '" + output + "'")
        print("Flag: " + str(flag) + " (Expected: " + str(expected_flag) + ")")
        print("Message: " + msg)
        assert flag == expected_flag, "Test failed for output: " + output

    print("\nAll safety checks passed (for current rules).")
