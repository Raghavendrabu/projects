import sys
sys.path.append("c:/Projects/birthday-assistant")
import pandas as pd
df = pd.read_excel("c:/Projects/birthday-assistant/data/people.xlsx", sheet_name="People")
import nlu, service, dialogue

questions = [
    "What are the upcoming birthdays?",
    "How many birthdays are there next month?",
    "Is there any birthday tomorrow?",
    "When is my wife's birthday?",
    "Any nephew birthdays in September?",
    "When is Rahul Patil's birthday?",
    "Count nephew birthdays in September",
    "Where does Rahul Patil stay?",
    "Show birthdays next month",
    "Hi"
]

for q in questions:
    p = nlu.parse(q, df)
    a = service.execute(p, df)
    print(f"Q: {q}\nParsed: {p}\nAns: {a}\n--")
