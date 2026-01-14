import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_technical_questions(tech_stack):
    prompt = f"""
You are a technical interviewer.

The candidate has the following tech stack:
{tech_stack}

Generate 1 technical interview questions per technology.
Return ONLY a JSON list of strings.

Example:
[
 "What is a Python list?",
 "Explain SQL joins",
 "What is Streamlit?"
]
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return json.loads(response.choices[0].message.content)
