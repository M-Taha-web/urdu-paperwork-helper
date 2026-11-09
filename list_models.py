import sys
from dotenv import load_dotenv
from google import genai

sys.stdout.reconfigure(encoding="utf-8")
load_dotenv()

client = genai.Client()
for m in client.models.list():
    print(m.name)