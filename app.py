import streamlit as st
import time
from llm import generate_technical_questions

# -------------------------------
# Page Setup
# -------------------------------
st.set_page_config(page_title="TalentScout – Hiring Assistant", layout="wide")
st.title("🤖 TalentScout – Hiring Assistant")

# -------------------------------
# Initialize Session State
# -------------------------------
if "stage" not in st.session_state:
    st.session_state.stage = "name"

if "candidate" not in st.session_state:
    st.session_state.candidate = {
        "name": "",
        "email": "",
        "phone": "",
        "location": "",
        "experience": "",
        "role": "",
        "tech_stack": ""
    }

if "messages" not in st.session_state:
    st.session_state.messages = []

if "waiting_for_reply" not in st.session_state:
    st.session_state.waiting_for_reply = False

if "pending_reply" not in st.session_state:
    st.session_state.pending_reply = ""

# -------------------------------
# Interview Flow
# -------------------------------
stages = [
    "name", "email", "phone", "location",
    "experience", "role", "tech_stack",
    "technical", "end"
]

questions = {
    "name": "What is your full name?",
    "email": "What is your email address?",
    "phone": "What is your phone number?",
    "location": "Where are you currently located?",
    "experience": "How many years of experience do you have?",
    "role": "What position are you applying for?",
    "tech_stack": "Please list your tech stack (languages, frameworks, tools)."
}

# -------------------------------
# Move to next stage
# -------------------------------
def go_next():
    idx = stages.index(st.session_state.stage)
    if idx + 1 < len(stages):
        st.session_state.stage = stages[idx + 1]

# -------------------------------
# Display Chat History
# -------------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -------------------------------
# Delayed assistant reply
# -------------------------------
if st.session_state.waiting_for_reply:
    with st.spinner("..."):
        time.sleep(0.5)

    st.session_state.messages.append({
        "role": "assistant",
        "content": st.session_state.pending_reply
    })

    st.session_state.pending_reply = ""
    st.session_state.waiting_for_reply = False
    st.rerun()

# -------------------------------
# Initial Greeting
# -------------------------------
if len(st.session_state.messages) == 0:
    intro = "Hello! I'm TalentScout, your AI hiring assistant.\n\n" + questions["name"]
    st.session_state.pending_reply = intro
    st.session_state.waiting_for_reply = True
    st.rerun()

# -------------------------------
# User Input
# -------------------------------
user_input = st.chat_input("Type here...")

if user_input:
    # Exit keywords
    if user_input.lower() in ["exit", "bye", "quit", "done"]:
        st.session_state.pending_reply = "Thank you for your time. Our recruitment team will contact you soon."
        st.session_state.waiting_for_reply = True
        st.session_state.stage = "end"
        st.rerun()

    # Store user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Save candidate info
    if st.session_state.stage in st.session_state.candidate:
        st.session_state.candidate[st.session_state.stage] = user_input
        go_next()

    # Decide reply
    if st.session_state.stage in questions:
        reply = questions[st.session_state.stage]

    elif st.session_state.stage == "technical":
        tech = st.session_state.candidate["tech_stack"]
        reply = generate_technical_questions(tech)
        go_next()

    else:
        reply = "Thank you for applying. We will be in touch."

    # Store reply for delayed display
    st.session_state.pending_reply = reply
    st.session_state.waiting_for_reply = True
    st.rerun()
