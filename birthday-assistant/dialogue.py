"""
dialogue.py - Conversational Dialogue State & Clarification Management
Exposes:
  - enrich_with_context(parsed, state)
  - update_state(parsed, state, last_result_ids=None)
"""

def enrich_with_context(parsed, state):
    """
    Carries over context attributes (month, relationship) from state only
    when the new user turn omits them.
    Also handles resolution of ambiguity when state has pending clarification
    and the user inputs a name or entity.
    """
    enriched_parsed = {
        "intent": parsed.get("intent", "unknown"),
        "entities": dict(parsed.get("entities", {}))
    }
    
    current_entities = enriched_parsed["entities"]
    state_entities = state.get("entities", {})
    
    # If intent is unknown but we have pending state, try to adopt prior intent
    if enriched_parsed["intent"] == "unknown" and state.get("last_intent"):
        if "month" in current_entities or "relationship" in current_entities or "person" in current_entities or "first_name" in current_entities:
            enriched_parsed["intent"] = state.get("last_intent")
            
    # Carry over relationship if not specified in current turn
    if "relationship" not in current_entities and "relationship" in state_entities:
        # Only carry over if we are not asking about a specific named person or specific non-related query
        if "person" not in current_entities and "person_id" not in current_entities:
            current_entities["relationship"] = state_entities["relationship"]
            
    # Carry over month if not specified in current turn
    if "month" not in current_entities and "date_expr" not in current_entities:
        # If user is asking a follow-up like "Who is my nephew?", keep the month if relevant
        if "month" in state_entities and ("person" not in current_entities and "person_id" not in current_entities):
            current_entities["month"] = state_entities["month"]

    return enriched_parsed

def update_state(parsed, state, last_result_ids=None):
    """
    Updates the dialogue session state with current intent, entities, and last_result_ids.
    """
    new_state = dict(state) if state else {}
    if "entities" not in new_state:
        new_state["entities"] = {}
        
    if parsed.get("intent") and parsed.get("intent") != "unknown":
        new_state["last_intent"] = parsed["intent"]
        
    # Merge entities
    for k, v in parsed.get("entities", {}).items():
        new_state["entities"][k] = v
        
    if last_result_ids is not None:
        new_state["last_result_ids"] = last_result_ids
        
    return new_state
