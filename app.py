import json
import os
from dotenv import load_dotenv
from flask import Flask, jsonify, request, render_template
from google import genai
from google.genai import types

load_dotenv()
app = Flask(__name__)

BASE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(BASE, "services.json"), encoding="utf-8") as f:
    SERVICES = json.load(f)

# Models to try, in order. If one is busy, the next is used.
MODELS = ["gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-3.8-flash"]

client = genai.Client(http_options=types.HttpOptions(timeout=30000))

SYSTEM_PROMPT = """You help people in Pakistan with government paperwork.
The user may write in English, Urdu script, or Roman Urdu.

Use ONLY the data below. Never invent documents, fees, counters or steps.
If a value says TODO or DRAFT, tell the user that detail is not confirmed
yet and they should check the official website.
If the question is not about a service in the data, set "found" to false.

Reply ONLY with JSON in exactly this shape:
{
  "found": true or false,
  "title_en": "service name in English",
  "title_ur": "service name in Urdu",
  "steps_en": ["short step 1", "short step 2"],
  "steps_ur": ["مختصر قدم 1", "مختصر قدم 2"]
}
Cover: documents to bring, which counters to visit in order (counter_steps),
where to go, and fees. Keep steps short and simple.
Each service has a "sample_fields" list. Any information from a field in that
list is demo placeholder data, not confirmed. When you use it, add "(Sample)"
at the end of that step in English and "(نمونہ)" in Urdu.
Always add a final step telling the user to confirm the details on the official
website (see "source" in the data), because fees and rules can change.

DATA:
""" + json.dumps(SERVICES, ensure_ascii=False)


def ask_ai(question):
    for name in MODELS:
        try:
            reply = client.models.generate_content(
                model=name,
                contents=question,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    response_mime_type="application/json",
                ),
            )
            return json.loads(reply.text)
        except Exception as e:
            print("Model failed:", name, type(e).__name__, str(e)[:100])
    return None


def find_service(text):
    text = text.lower()
    for service in SERVICES.values():
        for word in service["keywords"]:
            if word.lower() in text:
                return service
    return None


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():
    question = request.get_json().get("question", "").strip()
    if not question:
        return jsonify({"mode": "ai", "found": False})

    data = ask_ai(question)
    if data is not None:
        data["mode"] = "ai"
        return jsonify(data)

    # Backup: simple keyword matching if the AI is down
    service = find_service(question)
    if service is None:
        return jsonify({"mode": "keyword", "found": False})
    return jsonify({"mode": "keyword", "found": True, "service": service})


if __name__ == "__main__":
    app.run(debug=True)