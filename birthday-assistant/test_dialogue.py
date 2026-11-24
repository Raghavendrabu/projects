import sys
sys.path.append("c:/Projects/birthday-assistant")
import pandas as pd
df = pd.read_excel("c:/Projects/birthday-assistant/data/people.xlsx", sheet_name="People")
import dialogue, nlu, service, app

# Sequence A
s = {}
p1 = nlu.parse("Any nephew birthdays in September?", df)
p1 = dialogue.enrich_with_context(p1, s)
a1 = service.execute(p1, df)
s = dialogue.update_state(p1, s)

p2 = nlu.parse("What about October?", df)
p2 = dialogue.enrich_with_context(p2, s)
a2 = service.execute(p2, df)
s = dialogue.update_state(p2, s)

print("Sequence A:")
print("Turn 1:", a1)
print("Turn 2:", a2)

# Sequence B
s = {}
p_init = nlu.parse("When is my nephew's birthday?", df)
cp, ids = app.handle_ambiguity_check(p_init, df, "When is my nephew's birthday?")
s = dialogue.update_state(p_init, s, last_result_ids=ids)
res = app.check_pending_clarification("Nikhil", s, df)
if res:
    p_res = dialogue.enrich_with_context(res, s)
    a_res = service.execute(p_res, df)
else:
    # If ambiguous among nephews named Nikhil (Nikhil Hegde vs Nikhil Bhat)
    a_res = "Clarification needed among Nikhils"

print("\nSequence B:")
print("Clarification prompt:", cp)
print("Resolved:", res)
print("Answer:", a_res)

# Sequence C
s = {}
p1 = nlu.parse("Birthdays in September", df)
p1 = dialogue.enrich_with_context(p1, s)
a1 = service.execute(p1, df)
s = dialogue.update_state(p1, s)

# Reset session
s = {}
p2 = nlu.parse("What about October?", df)
p2 = dialogue.enrich_with_context(p2, s)
a2 = service.execute(p2, df)

print("\nSequence C:")
print("Turn 1 (count):", a1[:60], "...")
print("Turn 2 (after reset):", a2[:60], "...")
