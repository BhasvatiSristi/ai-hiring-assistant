import streamlit as st
import time
import json
from datetime import datetime
from llm import generate_technical_questions

st.set_page_config(page_title="TalentScout – Hiring Assistant", layout="wide")
st.title("🤖 TalentScout – Hiring Assistant")

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

# ---------------------------
# Interview flow
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
        st.session_state.completed = True
        st.session_state.stage = "end"

# ---------------------------
# Display chat
# ---------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------------------
# Delayed assistant reply
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
# Initial greeting
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

    # Technical interview mode
    if st.session_state.stage == "technical":
        st.session_state.current_q += 1

        if st.session_state.current_q < len(st.session_state.tech_questions):
            reply = st.session_state.tech_questions[st.session_state.current_q]
        else:
            finalize_interview()
            reply = "Thank you for completing the technical interview. We will be in touch."

    else:
        # Save normal fields
        if st.session_state.stage in st.session_state.candidate:
            st.session_state.candidate[st.session_state.stage] = user_input
            go_next()

        if st.session_state.stage in questions:
            reply = questions[st.session_state.stage]

        elif st.session_state.stage == "technical":
            # First show loading message
            st.session_state.messages.append({
                "role": "assistant",
                "content": "Please wait while we prepare your technical interview questions..."
            })
            
            tech = st.session_state.candidate["tech_stack"]

            # Generate questions
            st.session_state.tech_questions = generate_technical_questions(tech)
            st.session_state.current_q = 0

            # Ask first question
            reply = st.session_state.tech_questions[0]

        else:
            reply = "Thank you for applying."

    st.session_state.pending_reply = reply
    st.session_state.waiting_for_reply = True
    st.rerun()
