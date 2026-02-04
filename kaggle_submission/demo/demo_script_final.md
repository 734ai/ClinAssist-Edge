
# ClinAssist Edge - 3-Minute Demo Video Script

## Video Outline

**Total Time: ~3:00 minutes**

### 0:00–0:20 — Problem and Context (20 seconds)

*   **Visuals**: B-roll of a busy clinic or remote healthcare setting, possibly with limited resources. Overlay text: "Internet access unreliable? Privacy a concern? Clinicians overburdened?"
*   **Voiceover**: "In many healthcare settings, especially low-resource areas, constant internet access and centralized data infrastructure are luxuries. Clinicians need adaptable, privacy-focused AI tools that work offline, right at the point of care."
*   **Transition**: Fade to ClinAssist Edge logo.

### 0:20–1:10 — Live Demo (50 seconds)

*   **Visuals**: Screen recording of the Streamlit application.
    *   Show inputting patient data (e.g., "45-year-old male, fever 38.9C, productive cough, 3 days. SpO2 95%.") into the differential diagnosis text area.
    *   Click "Generate Differential Diagnosis & Red Flags". Show spinner.
    *   Display generated ranked differential, red flags.
    *   (Optional, if time permits): Quickly show inputting data for SOAP note and generating it.
*   **Voiceover**: "Enter ClinAssist Edge, your offline AI co-pilot. Built with Google's MedGemma, it runs entirely on local hardware. Here's how it works: just input patient symptoms... and instantly, our AI provides a ranked differential diagnosis, highlights critical red flags, and suggests next steps. It can also generate comprehensive SOAP notes and translate complex medical terms into patient-friendly instructions."

### 1:10–1:50 — Architecture & Privacy (40 seconds)

*   **Visuals**: Animated ASCII diagram from the write-up. Highlight "Local App", "MedGemma Inference (local)", "Local Storage". Show patient data icon staying within the device.
*   **Voiceover**: "The magic happens locally. ClinAssist Edge uses MedGemma and other HAI-DEF models, processing all sensitive patient data directly on your device. No cloud calls, no internet needed for inference, and encrypted local storage ensures unparalleled privacy and security."

### 1:50–2:30 — Safety & Evaluation (40 seconds)

*   **Visuals**: Show an example of the safety alert pop-up in the UI. Briefly display snippets of the evaluation notebook (e.g., DD accuracy results, a mock human evaluation survey screenshot).
*   **Voiceover**: "Patient safety is paramount. Our system includes rule-based safety gating to flag high-risk recommendations. Every AI-generated output requires human clinician review – it's a co-pilot, not a replacement. We rigorously evaluate performance against gold standards and human feedback, including metrics for diagnostic accuracy and patient instruction comprehension."

### 2:30–3:00 — Impact & Call-to-Action (30 seconds)

*   **Visuals**: Split screen: ClinAssist Edge UI alongside images of empowered clinicians, clear patient communication, possibly in diverse settings. End with ClinAssist Edge logo and a call to action.
*   **Voiceover**: "ClinAssist Edge empowers clinicians with accessible, intelligent support, reduces documentation burden, and improves patient understanding – all while preserving privacy. This is the future of human-centered AI in healthcare, today. Join us in making an impact. Learn more and contribute at our GitHub."

