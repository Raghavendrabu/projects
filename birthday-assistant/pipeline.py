"""
pipeline.py - Version dispatcher and execution coordinator for CIUX Birthday Assistant
Exposes:
  - dispatch(message, version, state, df) -> (reply_text, new_state, debug_dict)
Coordinates execution across V1, V2, V3, V4, and V5.
"""
import re
import pandas as pd
import v1_engine
import nlu
import service
import dialogue
import llm_nlu

def handle_ambiguity_check(parsed, df, message):
    """
    V3/V4 ambiguity check: if relationship present, person_id absent,
    question is singular ("when is my ...", "who is my ..."), and >1 match ->
    return clarification prompt and matched IDs.
    """
    rel = parsed.get("entities", {}).get("relationship")
    has_person = "person_id" in parsed.get("entities", {}) or "person" in parsed.get("entities", {})
    lower = message.lower()
    
    is_singular = bool(re.search(r'\b(when\s+is\s+my|who\s+is\s+my|where\s+does\s+my)\b', lower))
    
    if rel and not has_person and is_singular:
        matches = df[df["Relationship"].str.lower() == rel.lower()]
        if len(matches) > 1:
            names = ", ".join(matches["Name"].tolist()[:8])
            prompt = f"I found {len(matches)} people with that relationship: {names}. Which one do you mean?"
            matched_ids = matches["Person_ID"].tolist()
            return prompt, matched_ids
    return None, None

def check_pending_clarification(message, state, df):
    """
    Resolves previous ambiguity if user names one of the candidates stored in last_result_ids.
    """
    last_ids = state.get("last_result_ids") if state else None
    if last_ids and isinstance(last_ids, list):
        candidates = df[df["Person_ID"].isin(last_ids)]
        lower = message.lower().strip()
        for _, r in candidates.iterrows():
            name_parts = str(r["Name"]).lower().split()
            first_name = name_parts[0] if name_parts else ""
            full_name = str(r["Name"]).lower()
            nick = str(r["Nickname"]).lower() if pd.notna(r["Nickname"]) else ""
            
            if lower == full_name or lower == first_name or (nick and lower == nick):
                return {
                    "intent": state.get("last_intent", "birthday_search"),
                    "entities": {
                        "person": r["Name"],
                        "person_id": str(r["Person_ID"])
                    }
                }
    return None

def dispatch(message, version, state, df):
    """
    Dispatches incoming user message to the selected version pipeline.
    Returns: (reply, new_state, debug_dict)
    """
    ver = (version or "v5").lower()
    
    # -------------------------------------------------------------
    # Version 1: Monolithic Rule-Based Matcher (Brittle & Stateless)
    # -------------------------------------------------------------
    if ver == "v1":
        reply = v1_engine.execute_v1(message, df)
        debug = {
            "version": "V1 (Rule-Based Monolithic)",
            "source": "v1_regex_rules",
            "state_enabled": False,
            "note": "Brittle regex without NLU or state. Abbreviations like 'sept' or queries like 'birthday of Rahul' will fail."
        }
        return reply, {}, debug

    # -------------------------------------------------------------
    # Version 2: Decoupled Intent + Entity NLU (Stateless)
    # -------------------------------------------------------------
    if ver == "v2":
        parsed = nlu.parse(message, df)
        reply = service.execute(parsed, df)
        debug = {
            "version": "V2 (Intent + Entity NLU)",
            "source": "nlu_rules",
            "parsed": parsed,
            "state_enabled": False,
            "note": "Modular NLU and Service decoupled, but stateless: cannot carry context across turns."
        }
        return reply, {}, debug

    # -------------------------------------------------------------
    # Version 3: Dialogue State & Ambiguity Clarification
    # -------------------------------------------------------------
    if ver == "v3":
        curr_state = dict(state) if state else {}
        resolved_clarification = check_pending_clarification(message, curr_state, df)
        if resolved_clarification:
            parsed = resolved_clarification
            source = "clarification_resolved"
        else:
            parsed = nlu.parse(message, df)
            source = "nlu_rules"
            parsed = dialogue.enrich_with_context(parsed, curr_state)

        # Ambiguity check
        clarification_prompt, matched_ids = handle_ambiguity_check(parsed, df, message)
        if clarification_prompt:
            new_state = dialogue.update_state(parsed, curr_state, last_result_ids=matched_ids)
            debug = {
                "version": "V3 (Dialogue State & Clarification)",
                "source": source,
                "parsed": parsed,
                "state": new_state,
                "note": "Ambiguity detected! Clarification prompt issued and candidate IDs cached in session."
            }
            return clarification_prompt, new_state, debug

        reply = service.execute(parsed, df)
        new_state = dialogue.update_state(parsed, curr_state, last_result_ids=None)
        debug = {
            "version": "V3 (Dialogue State & Clarification)",
            "source": source,
            "parsed": parsed,
            "state": new_state,
            "note": "Dialogue state active: slot carryover and ambiguity clarification enabled."
        }
        return reply, new_state, debug

    # -------------------------------------------------------------
    # Version 4 & Version 5: Grounded LLM + Rules Fallback (+ Voice in V5)
    # -------------------------------------------------------------
    # V5 backend is identical to V4 as required by constraints
    curr_state = dict(state) if state else {}
    resolved_clarification = check_pending_clarification(message, curr_state, df)
    if resolved_clarification:
        parsed = resolved_clarification
        source = "clarification_resolved"
    else:
        llm_result = llm_nlu.llm_parse(message)
        if llm_result is not None and llm_nlu.validate(llm_result):
            parsed = llm_result
            source = "llm"
        else:
            parsed = nlu.parse(message, df)
            source = "rules_fallback"
        parsed = dialogue.enrich_with_context(parsed, curr_state)

    clarification_prompt, matched_ids = handle_ambiguity_check(parsed, df, message)
    if clarification_prompt:
        new_state = dialogue.update_state(parsed, curr_state, last_result_ids=matched_ids)
        debug = {
            "version": f"V{'5' if ver == 'v5' else '4'} ({'Multimodal Voice' if ver == 'v5' else 'Grounded LLM NLU'})",
            "source": source,
            "parsed": parsed,
            "state": new_state,
            "note": "Grounded execution: facts exclusively retrieved from Excel."
        }
        return clarification_prompt, new_state, debug

    reply = service.execute(parsed, df)
    new_state = dialogue.update_state(parsed, curr_state, last_result_ids=None)
    debug = {
        "version": f"V{'5' if ver == 'v5' else '4'} ({'Multimodal Voice' if ver == 'v5' else 'Grounded LLM NLU'})",
        "source": source,
        "parsed": parsed,
        "state": new_state,
        "note": "Grounded execution: facts exclusively retrieved from Excel."
    }
    return reply, new_state, debug
