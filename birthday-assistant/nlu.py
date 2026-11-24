"""
nlu.py - Natural Language Understanding layer for CIUX Birthday Assistant
Exposes: parse(message, df) -> {"intent": str, "entities": dict}
"""
import re
import datetime
import pandas as pd

MONTH_MAP = {
    "jan": 1, "january": 1,
    "feb": 2, "february": 2,
    "mar": 3, "march": 3,
    "apr": 4, "april": 4,
    "may": 5,
    "jun": 6, "june": 6,
    "jul": 7, "july": 7,
    "aug": 8, "august": 8,
    "sep": 9, "sept": 9, "september": 9,
    "oct": 10, "october": 10,
    "nov": 11, "november": 11,
    "dec": 12, "december": 12
}

RELATIONSHIP_ALIASES = {
    "wife": "Wife", "wives": "Wife", "spouse": "Wife",
    "father": "Father", "fathers": "Father", "dad": "Father", "papa": "Father",
    "mother": "Mother", "mothers": "Mother", "mom": "Mother", "mummy": "Mother",
    "nephew": "Nephew", "nephews": "Nephew",
    "niece": "Niece", "nieces": "Niece",
    "brother": "Brother", "brothers": "Brother",
    "sister": "Sister", "sisters": "Sister",
    "friend": "Friend", "friends": "Friend",
    "student": "Student", "students": "Student",
    "uncle": "Uncle", "uncles": "Uncle",
    "aunt": "Aunt", "aunts": "Aunt",
    "cousin": "Cousin", "cousins": "Cousin",
    "colleague": "Colleague", "colleagues": "Colleague", "coworker": "Colleague", "coworkers": "Colleague",
    "neighbour": "Neighbour", "neighbours": "Neighbour", "neighbor": "Neighbour", "neighbors": "Neighbour",
    "brother-in-law": "Brother-in-law", "brothers-in-law": "Brother-in-law", "brother in law": "Brother-in-law",
    "sister-in-law": "Sister-in-law", "sisters-in-law": "Sister-in-law", "sister in law": "Sister-in-law"
}

def extract_entities(text, df=None):
    entities = {}
    lower_text = text.lower().strip()
    
    # 1. Next N days (e.g. next 7 days, next 14 days)
    days_match = re.search(r'\bnext\s+(\d+)\s+days?\b', lower_text)
    if days_match:
        entities["days"] = int(days_match.group(1))
        
    # 2. Date expressions
    if re.search(r'\btomorrow\b', lower_text):
        entities["date_expr"] = "tomorrow"
    elif re.search(r'\bnext\s+month\b', lower_text):
        entities["date_expr"] = "next_month"
    elif re.search(r'\bthis\s+week\b', lower_text):
        entities["date_expr"] = "this_week"
    elif re.search(r'\bupcoming\b', lower_text):
        entities["date_expr"] = "upcoming"
        
    # 3. Month detection
    for m_str in sorted(MONTH_MAP.keys(), key=len, reverse=True):
        pattern = r'\b' + re.escape(m_str) + r'\b'
        if re.search(pattern, lower_text):
            entities["month"] = MONTH_MAP[m_str]
            break
            
    # 4. Relationship detection (case-insensitive singular/plural)
    for r_alias, canonical in sorted(RELATIONSHIP_ALIASES.items(), key=lambda x: len(x[0]), reverse=True):
        pattern = r'\b' + re.escape(r_alias) + r'\b'
        if re.search(pattern, lower_text):
            entities["relationship"] = canonical
            break
            
    # 5. Person detection (Full name, nickname, or partial first-name match from dataset)
    if df is not None and not df.empty:
        # Check full names first
        for _, row in df.iterrows():
            full_name = str(row["Name"]).strip()
            pattern = r'\b' + re.escape(full_name.lower()) + r'\b'
            if re.search(pattern, lower_text):
                entities["person"] = full_name
                entities["person_id"] = str(row["Person_ID"])
                break
                
        # If no full name match, check nicknames
        if "person" not in entities:
            for _, row in df.iterrows():
                nick = str(row["Nickname"]).strip() if pd.notna(row["Nickname"]) else ""
                if nick and len(nick) > 2:
                    pattern = r'\b' + re.escape(nick.lower()) + r'\b'
                    if re.search(pattern, lower_text):
                        entities["person"] = str(row["Name"]).strip()
                        entities["person_id"] = str(row["Person_ID"])
                        break
                        
        # If still no match, check partial first-name match
        if "person" not in entities:
            words = [w.strip("?,.!'\"") for w in lower_text.split()]
            skip_words = set(list(MONTH_MAP.keys()) + list(RELATIONSHIP_ALIASES.keys()) + [
                "when", "is", "my", "birthday", "bday", "birthdays", "what", "are", "the",
                "how", "many", "there", "any", "in", "on", "at", "where", "does", "stay",
                "live", "reside", "tell", "me", "show", "count", "next", "month", "tomorrow",
                "week", "days", "upcoming", "who", "was", "born", "about", "hi", "hello",
                "thanks", "thank", "you", "which", "one", "do", "mean"
            ])
            for word in words:
                if word in skip_words or len(word) < 3:
                    continue
                candidates = df[df["Name"].str.lower().str.startswith(word)]
                if len(candidates) == 1:
                    entities["person"] = candidates.iloc[0]["Name"]
                    entities["person_id"] = str(candidates.iloc[0]["Person_ID"])
                    break
                elif len(candidates) > 1:
                    entities["first_name"] = word.capitalize()
                    break

    # 6. Fallback extraction of named entity (e.g. "Einstein" in "When is Einstein's birthday?")
    if "person" not in entities and "relationship" not in entities:
        # Check patterns like "when is <person>'s birthday", "<person>'s birthday", "birthday of <person>"
        m_person = re.search(r"\bwhen\s+is\s+([a-zA-Z\s]+?)(?:'s)?\s+(?:birthday|bday)\b", lower_text)
        if not m_person:
            m_person = re.search(r"\b([a-zA-Z\s]+?)(?:'s)?\s+(?:birthday|bday)\b", lower_text)
        if not m_person:
            m_person = re.search(r"\b(?:birthday|bday)\s+of\s+([a-zA-Z\s]+)\b", lower_text)
        if not m_person:
            m_person = re.search(r"\bwhere\s+does\s+([a-zA-Z\s]+?)\s+stay\b", lower_text)

        if m_person:
            candidate = m_person.group(1).strip()
            # Clean up leading stop words like 'my', 'the', 'a'
            candidate = re.sub(r'^(my|the|a)\s+', '', candidate).strip()
            if candidate and candidate not in MONTH_MAP and candidate not in RELATIONSHIP_ALIASES:
                if len(candidate) >= 3 and not re.search(r'\b(any|upcoming|next|this)\b', candidate):
                    entities["person"] = candidate.title()

    return entities

def parse(message, df=None):
    """
    Parses a user natural language message into intent and entities.
    Returns: {"intent": str, "entities": dict}
    Allowed intents: birthday_search, count_birthdays, upcoming_birthdays, person_place, unknown
    """
    if not message or not isinstance(message, str):
        return {"intent": "unknown", "entities": {}}
        
    lower = message.lower().strip()
    entities = extract_entities(lower, df)
    
    # Greetings / Pleasantries -> unknown gracefully
    if re.fullmatch(r'(hi|hello|hey|thanks|thank you|good morning|good evening|good afternoon)\b.*', lower):
        return {"intent": "unknown", "entities": entities}
        
    # 1. person_place
    if re.search(r'\b(where\s+does|where\s+do|place\s+of\s+stay|where\s+is\s+.*stay|stay|lives?)\b', lower):
        if "person" in entities or "first_name" in entities or "relationship" in entities:
            return {"intent": "person_place", "entities": entities}
            
    # 2. count_birthdays
    if re.search(r'\b(how\s+many|count|number\s+of)\b', lower):
        return {"intent": "count_birthdays", "entities": entities}
        
    # 3. upcoming_birthdays
    if "days" in entities or entities.get("date_expr") in ["upcoming", "this_week", "tomorrow", "next_month"]:
        if re.search(r'\b(what\s+are|show|list|any|when|is\s+there)\b', lower) or "upcoming" in lower or "tomorrow" in lower:
            if "person" not in entities:
                return {"intent": "upcoming_birthdays", "entities": entities}
                
    # 4. birthday_search
    if re.search(r'\b(when|birthday|bday|birthdays|born|who\s+was\s+born|any\s+.*birthday|what\s+about)\b', lower):
        return {"intent": "birthday_search", "entities": entities}
        
    # 5. Direct single-slot follow-ups
    if "month" in entities or "relationship" in entities or "person" in entities or "first_name" in entities:
        return {"intent": "birthday_search", "entities": entities}
        
    return {"intent": "unknown", "entities": entities}
