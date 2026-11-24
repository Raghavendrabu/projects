# CIUX Birthday Assistant (Course UE24CS3540)
**Conversational Interfaces & User Experience — 5th Semester Project**

## Overview
CIUX Birthday Assistant is a 5-stage conversational web application designed to demonstrate the step-by-step evolution of conversational UX and Natural Language Understanding (NLU). The application is grounded strictly in a 100-row dataset (`data/people.xlsx`), ensuring zero hallucination.

An interactive **Architecture Dropdown Menu** in the header allows evaluators and students to toggle between all 5 versions (V1 through V5) live in the browser to test and observe how conversational limitations were discovered, logged, and solved.

---

## Architecture Versions Available via Dropdown

| Version | Name | How It Works | Key Failure / Limitation Observed |
| :--- | :--- | :--- | :--- |
| **V1** | **Rule-Based (Monolithic)** | Monolithic string & regex matching directly in routes. | **Brittle Pattern Matching:** Queries like `"birthday of Rahul"`, `"nephew birthdays in sept"`, or `"birthdays this week"` fail completely. |
| **V2** | **NLU + Service (Stateless)** | Decouples NLP parsing (`nlu.py`) into `{intent, entities}` and execution (`service.py`). | **State Amnesia:** Follow-up queries like `"What about October?"` lose the previous turn's relationship filter. |
| **V3** | **Dialogue State & Clarification** | Adds `dialogue.py` with Flask sessions to persist context and handle ambiguity. | Solves state amnesia and triggers clarification prompts when queries like `"When is my nephew's birthday?"` match multiple people (12 nephews). |
| **V4** | **Grounded LLM + Fallback** | Integrates LLM (`llm_nlu.py`) with strict JSON schema validation, offline rule fallback, and factual grounding. | **Hallucination Prevention:** The grounding barrier guarantees that queries about people not in the dataset (e.g., Einstein) are strictly refused. |
| **V5** | **Multimodal Voice** | Integrates client-side Web Speech API (STT via microphone + TTS voice readout). Backend unchanged. | Eliminates typing friction while maintaining 100% backend invariance. |

---

## Quick Start Instructions

### 1. Setup Environment
```powershell
cd c:\Projects\birthday-assistant
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Verify Dataset
The verified 100-row dataset is located at `data/people.xlsx`. You can verify primary key uniqueness at any time:
```powershell
python -c "import pandas as pd; df = pd.read_excel('data/people.xlsx', sheet_name='People'); print(f'{df[\"Person_ID\"].nunique()} unique, {df[\"Person_ID\"].duplicated().sum()} duplicates')"
```
Output:
```text
100 unique, 0 duplicates
```

### 3. Launch the Application
```powershell
python app.py
```
Open **`http://127.0.0.1:5000`** in Google Chrome or Microsoft Edge (recommended for Web Speech API support).

---

## Interactive Testing Guide via Dropdown

1. **Test V1 (Monolithic Rule-Based):**
   - Select **V1** from the dropdown.
   - Click the test chip `"birthday of Rahul"` → Observe failure: `"No matching birthdays found."` (requires exact full name).
   - Click `"nephew birthdays in sept"` → Observe failure (abbreviation not recognized).
   - Type `"When is Rahul Patil's birthday?"` → Observes success.

2. **Test V2 (Decoupled NLU & Service):**
   - Switch dropdown to **V2**.
   - Type `"Any nephew birthdays in September?"` → Receives 3 nephews.
   - Immediately follow up with `"What about October?"` → Notice state amnesia: dumps all 12 birthdays in October because V2 has no session memory.

3. **Test V3 (Dialogue State & Ambiguity Clarification):**
   - Switch dropdown to **V3**.
   - Click `"Reset"` to clear session.
   - Type `"Any nephew birthdays in September?"` followed by `"What about October?"` → Preserves `"Nephew"` relationship and returns Nikhil Hegde.
   - Type `"When is my nephew's birthday?"` → Receives clarification prompt: *"I found 12 people with that relationship: ... Which one do you mean?"*
   - Type `"Nikhil"` → Resolves ambiguity to Nikhil Hegde.

4. **Test V4 (Grounded LLM NLU):**
   - Switch dropdown to **V4**.
   - Click `"When is Einstein's birthday?"` → Observes refusal: `"I could not find that person in my records."` (No hallucination).

5. **Test V5 (Voice Multimodal):**
   - Switch dropdown to **V5**.
   - Click the **Microphone button** (pulses red while listening).
   - Speak: *"Is there any birthday tomorrow?"*
   - Assistant displays reply and speaks aloud via browser Text-to-Speech (`window.speechSynthesis`).
