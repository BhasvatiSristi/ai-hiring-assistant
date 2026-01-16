import json
from openai import OpenAI

client = OpenAI()

def generate_technical_questions(tech_stack: str):
    prompt = f"""
You are a technical interviewer.

Generate 5 technical interview questions based on the following tech stack:
{tech_stack}

IMPORTANT:
- Return ONLY a valid JSON array of strings.
- Do NOT add explanations.
- Do NOT use markdown.
- Example format:
[
  "Question 1?",
  "Question 2?"
]
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a strict JSON generator."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    raw_output = response.choices[0].message.content.strip()

    try:
        questions = json.loads(raw_output)

        # Safety check
        if not isinstance(questions, list):
            raise ValueError("JSON is not a list")

        return questions

    except Exception:
        # ✅ Fallback (never crash interview)
        return [
            f"Explain your experience with {tech_stack}.",
            f"What challenges have you faced while working with {tech_stack}?",
            f"How do you debug issues in {tech_stack} projects?",
            f"Explain a real-world project you built using {tech_stack}.",
            f"What best practices do you follow when working with {tech_stack}?"
        ]
