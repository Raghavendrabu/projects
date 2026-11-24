"""
app.py - Flask web application for CIUX Birthday Assistant
Routes: /, /chat, /reset
No business logic inside routes; delegates strictly to pipeline.
"""
import os
import pandas as pd
from flask import Flask, render_template, request, jsonify, session

import pipeline

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "ciux-birthday-assistant-secret-key-2026")

# Load people.xlsx dataset once
DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "people.xlsx")
if os.path.exists(DATA_PATH):
    df_people = pd.read_excel(DATA_PATH, sheet_name="People")
else:
    df_people = pd.DataFrame(columns=[
        "Person_ID", "Name", "Nickname", "DOB", "Place_of_Stay",
        "Relationship", "Relationship_Group", "Relationship_Detail", "Notes"
    ])

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json() or {}
    message = data.get("message", "").strip()
    version = data.get("version", "v5").strip().lower()

    if not message:
        return jsonify({"reply": "Please enter a message.", "debug": {}})

    state = session.get("dialogue_state", {})
    reply, new_state, debug = pipeline.dispatch(message, version, state, df_people)
    session["dialogue_state"] = new_state

    return jsonify({"reply": reply, "debug": debug})

@app.route("/reset", methods=["POST"])
def reset():
    session.pop("dialogue_state", None)
    return jsonify({"status": "Session reset successful.", "reply": "Conversation reset."})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
