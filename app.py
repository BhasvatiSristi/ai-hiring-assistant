import streamlit as st
import time
import json
import re
from datetime import datetime
from styles import load_styles
from llm import generate_technical_questions
import os
import requests

def send_email(candidate):
    url = os.getenv("MAKE_WEBHOOK") or "https://hook.eu1.make.com/wk9cdh1cegely8ujx241eit4631p88ah"
    try:
        requests.post(url, json={
            "name": candidate.get("name"),
            "email": candidate.get("email"),
            "role": candidate.get("role")
        })
    except:
        pass


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
# Session State
# ---------------------------
if "stage" not in st.session_state:
    st.session_state.stage = "name"

if "candidate" not in st.session_state:
    st.session_state.candidate = {
        "name": "", "email": "", "phone": "",
        "location": "", "experience": "",
        "role": "", "tech_stack": ""
    }

if "messages" not in st.session_state:
    st.session_state.messages = []

if "waiting_for_reply" not in st.session_state:
    st.session_state.waiting_for_reply = False

if "pending_reply" not in st.session_state:
    st.session_state.pending_reply = ""

if "tech_questions" not in st.session_state:
    st.session_state.tech_questions = []

if "current_q" not in st.session_state:
    st.session_state.current_q = 0

if "completed" not in st.session_state:
    st.session_state.completed = False

if "tech_loading" not in st.session_state:
    st.session_state.tech_loading = False

# ---------------------------
# Interview Flow
# ---------------------------
stages = ["name", "email", "phone", "location", "experience", "role", "tech_stack", "technical", "end"]

questions = {
    "name": "What is your full name?",
    "email": "What is your email address?",
    "phone": "What is your phone number?",
    "location": "Where are you currently located?",
    "experience": "How many years of experience do you have?",
    "role": "What position are you applying for?",
    "tech_stack": "Please list your tech stack (languages, frameworks, tools)."
}

def go_next():
    idx = stages.index(st.session_state.stage)
    if idx + 1 < len(stages):
        st.session_state.stage = stages[idx + 1]

def save_candidate(candidate):
    candidate_copy = candidate.copy()
    candidate_copy["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        with open("data/candidates.json", "r") as f:
            data = json.load(f)
    except:
        data = []

    data.append(candidate_copy)

    with open("data/candidates.json", "w") as f:
        json.dump(data, f, indent=4)

def finalize_interview():
    if not st.session_state.completed:
        save_candidate(st.session_state.candidate)
        send_email(st.session_state.candidate)   # <-- this line sends email
        st.session_state.completed = True
        st.session_state.stage = "end"


# ---------------------------
# Display Chat
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
    intro = "Hello! I'm TalentScout, your AI hiring assistant.\n\n" + questions["name"]
    st.session_state.pending_reply = intro
    st.session_state.waiting_for_reply = True
    st.rerun()

# ---------------------------
# User Input
# ---------------------------
if not st.session_state.completed:
    user_input = st.chat_input("Type here...")
else:
    user_input = None

if user_input:
    if user_input.lower() in ["exit", "bye", "quit", "done"]:
        finalize_interview()
        st.session_state.pending_reply = "Thank you for your time. Our recruitment team will contact you soon."
        st.session_state.waiting_for_reply = True
        st.rerun()

    st.session_state.messages.append({"role": "user", "content": user_input})

    reply = None

    # Technical interview mode
    if st.session_state.stage == "technical":
        if st.session_state.tech_loading:
            tech = st.session_state.candidate["tech_stack"]
            st.session_state.tech_questions = generate_technical_questions(tech)
            st.session_state.current_q = 0
            st.session_state.tech_loading = False
            reply = st.session_state.tech_questions[0]
        else:
            st.session_state.current_q += 1
            if st.session_state.current_q < len(st.session_state.tech_questions):
                reply = st.session_state.tech_questions[st.session_state.current_q]
            else:
                finalize_interview()
                reply = "Thank you for completing the technical interview. We will be in touch."

    else:
        # Validation
        if st.session_state.stage == "email" and not is_valid_email(user_input):
            reply = "Please enter a valid email address."
        elif st.session_state.stage == "phone" and not is_valid_phone(user_input):
            reply = "Please enter a valid phone number."
        elif st.session_state.stage == "experience" and not is_valid_experience(user_input):
            reply = "Please enter your years of experience as a number."
        elif st.session_state.stage in ["role", "location"] and not is_valid_text(user_input):
            reply = f"Please enter a valid {st.session_state.stage}."
        else:
            if st.session_state.stage in st.session_state.candidate:
                st.session_state.candidate[st.session_state.stage] = user_input
                go_next()

            if st.session_state.stage in questions:
                reply = questions[st.session_state.stage]
            elif st.session_state.stage == "technical":
                # Show loading message once
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "Please wait while we prepare your technical interview questions..."
                })

                # Generate questions
                tech = st.session_state.candidate["tech_stack"]
                st.session_state.tech_questions = generate_technical_questions(tech)
                st.session_state.current_q = 0

                # Ask first technical question
                reply = st.session_state.tech_questions[0]


    st.session_state.pending_reply = reply
    st.session_state.waiting_for_reply = True
    st.rerun()

