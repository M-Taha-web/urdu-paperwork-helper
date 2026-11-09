import json
import os
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

BASE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(BASE, "services.json"), encoding="utf-8") as f:
    SERVICES = json.load(f)


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
    question = request.get_json().get("question", "")
    service = find_service(question)
    if service is None:
        return jsonify({"found": False})
    return jsonify({"found": True, "service": service})


@app.route("/services")
def services():
    return jsonify(SERVICES)


if __name__ == "__main__":
    app.run(debug=True)