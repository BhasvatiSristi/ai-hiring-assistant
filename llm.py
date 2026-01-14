import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_technical_questions(tech_stack):
    prompt = f"""
You are a technical interviewer for a hiring platform.

The candidate has the following tech stack:
{tech_stack}

Generate 3 to 5 technical interview questions for each technology.
Use clear headings for each technology.
Questions should be junior to mid-level.
Avoid yes/no questions.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content
