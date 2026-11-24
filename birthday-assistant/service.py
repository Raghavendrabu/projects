"""
service.py - Query and formatting service for CIUX Birthday Assistant
Exposes: execute(parsed, df) -> str and fmt_people(rows)
Reference evaluation date: TODAY = 2026-11-19
"""
import datetime
import pandas as pd

# Hardcoded reference date as mandated by the evaluation spec
TODAY = datetime.date(2026, 11, 19)

def fmt_date(d):
    """Format datetime.date or Timestamp into 'DD Month YYYY'"""
    if isinstance(d, str):
        try:
            d = datetime.datetime.strptime(d, "%Y-%m-%d").date()
        except:
            return d
    elif isinstance(d, pd.Timestamp):
        d = d.date()
    return d.strftime("%d %B %Y")

def fmt_people(rows):
    """Format a dataframe or list of rows into a readable response string."""
    if rows is None or len(rows) == 0:
        return "No matching people found."
    lines = []
    for _, r in rows.iterrows():
        bday_str = fmt_date(r["DOB"])
        rel = r.get("Relationship", "")
        place = r.get("Place_of_Stay", "")
        rel_str = f" ({rel})" if rel else ""
        lines.append(f"{r['Name']}{rel_str} - {bday_str}, stays in {place}")
    return "\n".join(lines)

def execute(parsed, df):
    """
    Executes the query given parsed intent and entities against df.
    Returns: formatted response string.
    """
    intent = parsed.get("intent", "unknown")
    entities = parsed.get("entities", {})
    
    if intent == "unknown":
        return "I'm sorry, I didn't understand that. You can ask me about birthdays (e.g., 'When is Rahul Patil's birthday?', 'Any nephew birthdays in September?', 'Upcoming birthdays')."
        
    # --- Intent: person_place ---
    if intent == "person_place":
        if "person_id" in entities:
            match = df[df["Person_ID"] == entities["person_id"]]
            if not match.empty:
                r = match.iloc[0]
                return f"{r['Name']} stays in {r['Place_of_Stay']}."
        if "person" in entities:
            match = df[df["Name"].str.lower() == entities["person"].lower()]
            if not match.empty:
                r = match.iloc[0]
                return f"{r['Name']} stays in {r['Place_of_Stay']}."
        if "first_name" in entities:
            matches = df[df["Name"].str.lower().str.startswith(entities["first_name"].lower())]
            if len(matches) > 1:
                names = ", ".join(matches["Name"].tolist()[:8])
                return f"Multiple people named {entities['first_name']} found: {names}. Which one do you mean?"
            elif len(matches) == 1:
                r = matches.iloc[0]
                return f"{r['Name']} stays in {r['Place_of_Stay']}."
        return "I could not find that person in my records."

    # --- Intent: birthday_search ---
    if intent == "birthday_search":
        # 1. By Person ID or Person Name
        if "person_id" in entities:
            match = df[df["Person_ID"] == entities["person_id"]]
            if not match.empty:
                r = match.iloc[0]
                return f"{r['Name']}'s birthday is on {fmt_date(r['DOB'])}."
            return "I could not find that person in my records."
            
        if "person" in entities:
            match = df[df["Name"].str.lower() == entities["person"].lower()]
            if not match.empty:
                r = match.iloc[0]
                return f"{r['Name']}'s birthday is on {fmt_date(r['DOB'])}."
            return "I could not find that person in my records."

        # Filter by relationship and/or month
        filtered = df.copy()
        
        # Ensure DOB is datetime
        dob_dt = pd.to_datetime(filtered["DOB"])
        
        rel = entities.get("relationship")
        month = entities.get("month")
        
        if rel:
            filtered = filtered[filtered["Relationship"].str.lower() == rel.lower()]
            
        if month:
            filtered = filtered[pd.to_datetime(filtered["DOB"]).dt.month == int(month)]
            
        if "date_expr" in entities and entities["date_expr"] == "tomorrow":
            t_month = (TODAY + datetime.timedelta(days=1)).month
            t_day = (TODAY + datetime.timedelta(days=1)).day
            filtered = filtered[(pd.to_datetime(filtered["DOB"]).dt.month == t_month) & 
                                (pd.to_datetime(filtered["DOB"]).dt.day == t_day)]
                                
        if filtered.empty:
            if rel and month:
                return f"No {rel.lower()} birthdays found in that month."
            elif rel:
                return f"No {rel.lower()} birthdays found in my records."
            elif month:
                return f"No birthdays found in that month."
            return "No matching birthdays found."
            
        if len(filtered) == 1:
            r = filtered.iloc[0]
            return f"{r['Name']}'s birthday is on {fmt_date(r['DOB'])}."
            
        # Multiple matches
        formatted = []
        for _, r in filtered.iterrows():
            formatted.append(f"{r['Name']} ({fmt_date(r['DOB'])})")
        return f"Found {len(filtered)} birthdays: " + ", ".join(formatted) + "."

    # --- Intent: count_birthdays ---
    if intent == "count_birthdays":
        filtered = df.copy()
        rel = entities.get("relationship")
        month = entities.get("month")
        date_expr = entities.get("date_expr")
        
        if rel:
            filtered = filtered[filtered["Relationship"].str.lower() == rel.lower()]
            
        if month:
            filtered = filtered[pd.to_datetime(filtered["DOB"]).dt.month == int(month)]
            rel_phrase = f"{rel.lower()} " if rel else ""
            month_name = datetime.date(2026, int(month), 1).strftime("%B")
            return f"There are {len(filtered)} {rel_phrase}birthdays in {month_name}."
            
        if date_expr == "next_month":
            nm = 12 if TODAY.month == 11 else (TODAY.month % 12 + 1)
            filtered = filtered[pd.to_datetime(filtered["DOB"]).dt.month == nm]
            nm_name = datetime.date(2026, nm, 1).strftime("%B")
            return f"There are {len(filtered)} birthdays next month ({nm_name})."
            
        if date_expr == "tomorrow":
            t_month = (TODAY + datetime.timedelta(days=1)).month
            t_day = (TODAY + datetime.timedelta(days=1)).day
            filtered = filtered[(pd.to_datetime(filtered["DOB"]).dt.month == t_month) & 
                                (pd.to_datetime(filtered["DOB"]).dt.day == t_day)]
            return f"There are {len(filtered)} birthdays tomorrow."
            
        return f"Total matching birthdays: {len(filtered)}."

    # --- Intent: upcoming_birthdays ---
    if intent == "upcoming_birthdays":
        date_expr = entities.get("date_expr")
        days_window = entities.get("days")
        
        if date_expr == "tomorrow":
            target = TODAY + datetime.timedelta(days=1)
            matches = df[(pd.to_datetime(df["DOB"]).dt.month == target.month) & 
                         (pd.to_datetime(df["DOB"]).dt.day == target.day)]
            if matches.empty:
                return "There are no birthdays tomorrow."
            names = ", ".join([f"{r['Name']} ({r['Relationship']})" for _, r in matches.iterrows()])
            return f"Yes! Tomorrow ({fmt_date(target)}) is: {names}."
            
        if date_expr == "next_month":
            nm = 12 if TODAY.month == 11 else (TODAY.month % 12 + 1)
            matches = df[pd.to_datetime(df["DOB"]).dt.month == nm]
            if matches.empty:
                return "There are no birthdays next month."
            summary = [f"{r['Name']} on {fmt_date(r['DOB'])}" for _, r in matches.iterrows()]
            return f"Birthdays next month ({datetime.date(2026, nm, 1).strftime('%B')}):\n" + "\n".join(summary)
            
        # Upcoming in next N days or generic upcoming (default to next 14 days)
        window = days_window if days_window else 14
        upcoming_rows = []
        for _, row in df.iterrows():
            dob = pd.to_datetime(row["DOB"]).date()
            # Construct this year's birthday
            try:
                bday_this_year = datetime.date(TODAY.year, dob.month, dob.day)
            except ValueError:
                # Leap day February 29 on non-leap year
                bday_this_year = datetime.date(TODAY.year, 2, 28)
                
            delta = (bday_this_year - TODAY).days
            if delta < 0:
                # Check next year
                try:
                    bday_next_year = datetime.date(TODAY.year + 1, dob.month, dob.day)
                except ValueError:
                    bday_next_year = datetime.date(TODAY.year + 1, 2, 28)
                delta = (bday_next_year - TODAY).days
                
            if 0 <= delta <= window:
                upcoming_rows.append((delta, row))
                
        if not upcoming_rows:
            return f"No birthdays found in the next {window} days."
            
        upcoming_rows.sort(key=lambda x: x[0])
        lines = []
        for delta, r in upcoming_rows:
            day_str = "today" if delta == 0 else ("tomorrow" if delta == 1 else f"in {delta} days")
            lines.append(f"{r['Name']} ({r['Relationship']}) - {fmt_date(r['DOB'])} ({day_str})")
        return f"Upcoming birthdays in the next {window} days:\n" + "\n".join(lines)

    return "No matching records found."
