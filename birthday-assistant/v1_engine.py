"""
v1_engine.py - Version 1 Deterministic Rule-Based Engine (Monolithic simulation)
Implements the exact brittle regex, hardcoded string matching, and failure cases
documented in Section 4 of the report.
"""
import re
import datetime
import pandas as pd

TODAY = datetime.date(2026, 11, 19)

# V1 hardcoded month list (only full month names, lacks abbreviations like 'sept' or 'sep')
V1_MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12
}

def execute_v1(message, df):
    """
    Executes raw string matching conditionals without NLU entity extraction or dialogue state.
    Reproduces the exact V1 pass and fail behaviors.
    """
    lower = message.lower().strip()

    # V1: Exact phrase "What are the upcoming birthdays?" or "upcoming birthdays"
    if "upcoming birthdays" in lower or "what are the upcoming" in lower:
        # Hardcoded 14-day upcoming scan
        upcoming_rows = []
        for _, row in df.iterrows():
            dob = pd.to_datetime(row["DOB"]).date()
            try:
                bday_this_year = datetime.date(TODAY.year, dob.month, dob.day)
            except ValueError:
                bday_this_year = datetime.date(TODAY.year, 2, 28)
            delta = (bday_this_year - TODAY).days
            if delta < 0:
                try:
                    bday_next_year = datetime.date(TODAY.year + 1, dob.month, dob.day)
                except ValueError:
                    bday_next_year = datetime.date(TODAY.year + 1, 2, 28)
                delta = (bday_next_year - TODAY).days
            if 0 <= delta <= 14:
                upcoming_rows.append((delta, row))
        upcoming_rows.sort(key=lambda x: x[0])
        lines = []
        for delta, r in upcoming_rows:
            day_str = "today" if delta == 0 else ("tomorrow" if delta == 1 else f"in {delta} days")
            lines.append(f"{r['Name']} ({r['Relationship']}) - {pd.to_datetime(r['DOB']).strftime('%d %B %Y')} ({day_str})")
        return "Upcoming birthdays in the next 14 days:\n" + "\n".join(lines)

    # V1: "How many birthdays are there next month?"
    if "how many birthdays" in lower and "next month" in lower:
        nm = 12 if TODAY.month == 11 else (TODAY.month % 12 + 1)
        matches = df[pd.to_datetime(df["DOB"]).dt.month == nm]
        return f"There are {len(matches)} birthdays next month (December)."

    # V1: "Is there any birthday tomorrow?"
    if "birthday tomorrow" in lower or "any birthday tomorrow" in lower:
        target = TODAY + datetime.timedelta(days=1)
        matches = df[(pd.to_datetime(df["DOB"]).dt.month == target.month) & 
                     (pd.to_datetime(df["DOB"]).dt.day == target.day)]
        if matches.empty:
            return "There are no birthdays tomorrow."
        names = ", ".join([f"{r['Name']} ({r['Relationship']})" for _, r in matches.iterrows()])
        return f"Yes! Tomorrow ({target.strftime('%d %B %Y')}) is: {names}."

    # V1: "When is my wife's birthday?" or "wife birthday"
    if "wife" in lower and ("birthday" in lower or "when" in lower):
        matches = df[df["Relationship"].str.lower() == "wife"]
        if not matches.empty:
            formatted = [f"{r['Name']} ({pd.to_datetime(r['DOB']).strftime('%d %B %Y')})" for _, r in matches.iterrows()]
            return f"Found {len(matches)} birthdays: " + ", ".join(formatted) + "."
        return "No wife birthdays found in my records."

    # V1: "Any nephew birthdays in September?"
    # Note: V1 required exact full month "september". "sept" will fail!
    if "nephew" in lower and ("birthday" in lower or "any" in lower):
        found_month = None
        for m_name, m_num in V1_MONTHS.items():
            if re.search(r'\b' + m_name + r'\b', lower):
                found_month = m_num
                break
        if found_month:
            matches = df[(df["Relationship"].str.lower() == "nephew") & 
                         (pd.to_datetime(df["DOB"]).dt.month == found_month)]
            if not matches.empty:
                formatted = [f"{r['Name']} ({pd.to_datetime(r['DOB']).strftime('%d %B %Y')})" for _, r in matches.iterrows()]
                return f"Found {len(matches)} birthdays: " + ", ".join(formatted) + "."
            return "No nephew birthdays found in that month."
        elif "sept" in lower or "oct" in lower:
            # Fails because abbreviation is not in V1_MONTHS
            return "No matching birthdays found."

    # V1: "When is Rahul Patil's birthday?"
    # Note: Demanded full name "Rahul Patil". "birthday of Rahul" fails!
    for _, r in df.iterrows():
        full_name = str(r["Name"]).lower()
        if full_name in lower and ("birthday" in lower or "when" in lower):
            b_str = pd.to_datetime(r["DOB"]).strftime("%d %B %Y")
            return f"{r['Name']}'s birthday is on {b_str}."

    # V1 failure on partial name like "birthday of Rahul"
    if "birthday" in lower and "rahul" in lower and "rahul patil" not in lower:
        return "No matching birthdays found."

    # V1 failure on unhandled patterns
    return "I'm sorry, I didn't understand that. You can ask me about birthdays (e.g., 'When is Rahul Patil's birthday?', 'Any nephew birthdays in September?', 'Upcoming birthdays')."
