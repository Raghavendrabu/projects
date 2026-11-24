"""
llm_nlu.py - LLM-based NLU layer with strict validation and offline fallback.
Exposes:
  - llm_parse(message) -> dict | None
  - validate(parsed) -> bool
"""
import os
import json
import re

ALLOWED_INTENTS = {"birthday_search", "count_birthdays", "upcoming_birthdays", "person_place", "unknown"}
ALLOWED_ENTITY_KEYS = {"person", "person_id", "first_name", "relationship", "month", "date_expr", "days"}

def validate(parsed):
    """
    Validation layer:
    1. Must be a dictionary.
    2. Must contain 'intent' and 'entities'.
    3. 'intent' must be one of ALLOWED_INTENTS.
    4. 'entities' must be a dict whose keys belong to ALLOWED_ENTITY_KEYS.
    5. Rejects any LLM hallucinations or unstructured prose.
    """
    if not isinstance(parsed, dict):
        return False
    if "intent" not in parsed or "entities" not in parsed:
        return False
    if parsed["intent"] not in ALLOWED_INTENTS:
        return False
    if not isinstance(parsed["entities"], dict):
        return False
    for k in parsed["entities"].keys():
        if k not in ALLOWED_ENTITY_KEYS:
            return False
    return True

def llm_parse(message):
    """
    Calls OpenAI or Anthropic API if environment variables are set.
    Prompt strictly constrains LLM to return only JSON with intent and entities.
    The LLM NEVER generates factual answers, dates, or birthdays.
    If no API key is set, returns None to trigger deterministic fallback.
    """
    openai_key = os.environ.get("OPENAI_API_KEY")
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    
    if not openai_key and not anthropic_key:
        # Offline mode: silently return None so app falls back to nlu.parse
        return None
        
    system_prompt = (
        "You are an NLU parser for a Birthday Assistant. Given a user query, "
        "extract intent and entities and respond ONLY with a raw JSON object.\n"
        "Allowed intents: 'birthday_search', 'count_birthdays', 'upcoming_birthdays', 'person_place', 'unknown'.\n"
        "Allowed entity keys: 'person' (string), 'relationship' (canonical singular title e.g. Nephew, Wife), "
        "'month' (integer 1-12), 'date_expr' (string: 'tomorrow', 'next_month', 'this_week', 'upcoming'), "
        "'days' (integer).\n"
        "Do NOT provide explanations or conversational text. Return ONLY JSON."
    )
    
    try:
        if openai_key:
            import requests
            headers = {
                "Authorization": f"Bearer {openai_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                "temperature": 0.0,
                "response_format": {"type": "json_object"}
            }
            res = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=5)
            if res.status_code == 200:
                content = res.json()["choices"][0]["message"]["content"]
                parsed = json.loads(content)
                if validate(parsed):
                    return parsed
        elif anthropic_key:
            import requests
            headers = {
                "x-api-key": anthropic_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "claude-3-haiku-20240307",
                "max_tokens": 200,
                "system": system_prompt,
                "messages": [{"role": "user", "content": message}]
            }
            res = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload, timeout=5)
            if res.status_code == 200:
                content = res.json()["content"][0]["text"]
                # Extract json substring
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    parsed = json.loads(json_match.group(0))
                    if validate(parsed):
                        return parsed
    except Exception:
        # Any network or parsing issue triggers graceful fallback
        return None
        
    return None
