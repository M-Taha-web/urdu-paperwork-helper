import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types

sys.stdout.reconfigure(encoding="utf-8")
load_dotenv()

MODELS = ["gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-3.8-flash"]

client = genai.Client(http_options=types.HttpOptions(timeout=30000))

for name in MODELS:
    try:
        print("Trying", name, "...")
        reply = client.models.generate_content(
            model=name,
            contents="Say hello in Urdu and English, one line.",
        )
        print("WORKED:", reply.text)
        break
    except Exception as e:
        print("Failed:", type(e).__name__, str(e)[:100])