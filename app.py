import streamlit as st
import time
import json
import re
from datetime import datetime
import requests
from styles import load_styles
from llm import generate_technical_questions
from time_utils import start_timer, stop_timer, get_total_time

# ---------------------------
# Page Setup
# ---------------------------
st.set_page_config(page_title="TalentScout – Hiring Assistant", layout="wide")
load_styles()
st.title("🤖 TalentScout – Hiring Assistant")

# ---------------------------
# Validators
# ---------------------------
def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def is_valid_phone(phone):
    return phone.isdigit() and 10 <= len(phone) <= 12

def is_valid_experience(exp):
    try:
        float(exp)
        return True
    except:
        return False

def is_valid_text(text):
    return bool(re.match(r"^[A-Za-z .-]{2,}$", text.strip()))

# ---------------------------
# Session State Initialization
# ---------------------------
defaults = {
    "stage": "name",
    "messages": [],
    "waiting_for_reply": False,
    "pending_reply": "",
    "current_q": 0,
    "tech_questions": [],
    "tech_loading": False,
    "completed": False,
    "tech_timings": [],
    "technical_answers": []
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

if "candidate" not in st.session_state:
    st.session_state.candidate = {
        "name": "", "email": "", "phone": "",
        "location": "", "experience": "",
        "role": "", "tech_stack": "",
        "confidence": "", "feedback": ""
    }

# ---------------------------
# Interview Flow
# ---------------------------
stages = [
    "name", "email", "phone", "location",
    "experience", "role", "tech_stack",
    "technical", "confidence", "feedback", "end"
]

questions = {
    "name": "What is your full name?",
    "email": "What is your email address?",
    "phone": "What is your phone number?",
    "location": "Where are you currently located?",
    "experience": "How many years of experience do you have?",
    "role": "What position are you applying for?",
    "tech_stack": "Please list your tech stack (languages, frameworks, tools).",
    "confidence": "On a scale of 1–5, how confident are you with your technical answers?",
    "feedback": "How was your experience with TalentScout? (Optional)"
}

def go_next():
    st.session_state.stage = stages[stages.index(st.session_state.stage) + 1]

def save_candidate():
    record = st.session_state.candidate.copy()
    record["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    record["technical_interview"] = st.session_state.technical_answers
    record["total_technical_time_seconds"] = get_total_time()

    try:
        with open("data/candidates.json", "r") as f:
            data = json.load(f)
    except:
        data = []

    data.append(record)

    with open("data/candidates.json", "w") as f:
        json.dump(data, f, indent=4)

def finalize_interview():
    if not st.session_state.completed:
        save_candidate()

        # Send email trigger to Make
        try:
            requests.post(
                "https://hook.eu1.make.com/wk9cdh1cegely8ujx241eit4631p88ah",
                json={
                    "email": st.session_state.candidate["email"]
                },
                timeout=5
            )
        except Exception as e:
            print("Make webhook failed:", e)

        st.session_state.completed = True
        st.session_state.stage = "end"


# ---------------------------
# Display Chat History
# ---------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------------------
# Delayed Assistant Reply
# ---------------------------
if st.session_state.waiting_for_reply:
    with st.spinner("TalentScout is thinking..."):
        time.sleep(1)

    st.session_state.messages.append({
        "role": "assistant",
        "content": st.session_state.pending_reply
    })

    st.session_state.pending_reply = ""
    st.session_state.waiting_for_reply = False
    st.rerun()

# ---------------------------
# Initial Greeting
# ---------------------------
if len(st.session_state.messages) == 0:
    intro = (
        "Hello! I'm TalentScout, your AI hiring assistant.\n\n"
        + questions["name"]
    )
    st.session_state.pending_reply = intro
    st.session_state.waiting_for_reply = True
    st.rerun()

# ---------------------------
# User Input
# ---------------------------
user_input = None if st.session_state.completed else st.chat_input("Type here...")

if user_input:
    if user_input.lower() in ["exit", "quit", "bye"]:
        finalize_interview()
        st.session_state.pending_reply = (
            "Thank you for your time. Our recruitment team will contact you soon."
        )
        st.session_state.waiting_for_reply = True
        st.rerun()

    st.session_state.messages.append({"role": "user", "content": user_input})
    reply = None

    # ---------------------------
    # Technical Interview Stage
    # ---------------------------
    if st.session_state.stage == "technical":

        current_question = st.session_state.tech_questions[st.session_state.current_q]
        stop_timer(current_question)

        st.session_state.technical_answers.append({
            "question": current_question,
            "answer": user_input
        })

        st.session_state.current_q += 1

        if st.session_state.current_q < len(st.session_state.tech_questions):
            reply = st.session_state.tech_questions[st.session_state.current_q]
            start_timer()
        else:
            go_next()
            reply = questions["confidence"]

    # ---------------------------
    # Validation + Normal Flow
    # ---------------------------
    else:
        stage = st.session_state.stage

        if stage == "email" and not is_valid_email(user_input):
            reply = "Please enter a valid email address."
        elif stage == "phone" and not is_valid_phone(user_input):
            reply = "Please enter a valid phone number."
        elif stage == "experience" and not is_valid_experience(user_input):
            reply = "Please enter years of experience as a number."
        elif stage in ["role", "location"] and not is_valid_text(user_input):
            reply = f"Please enter a valid {stage}."
        else:
            st.session_state.candidate[stage] = user_input

            if stage == "tech_stack":
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "Please wait while we prepare your technical interview questions..."
                })

                st.session_state.tech_questions = generate_technical_questions(user_input)
                st.session_state.current_q = 0
                go_next()
                reply = st.session_state.tech_questions[0]
                start_timer()

            elif stage == "feedback":
                finalize_interview()
                reply = (
                    "Thank you for your time. Our recruitment team will contact you soon."
                )

            else:
                go_next()
                reply = questions.get(st.session_state.stage)

    if reply:
        st.session_state.pending_reply = reply
        st.session_state.waiting_for_reply = True
        st.rerun()
