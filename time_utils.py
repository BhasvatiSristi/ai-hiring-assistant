import time
import streamlit as st

def start_timer():
    st.session_state.question_start_time = time.time()

def stop_timer(question):
    if "question_start_time" not in st.session_state:
        return

    elapsed = round(time.time() - st.session_state.question_start_time, 2)

    if "tech_timings" not in st.session_state:
        st.session_state.tech_timings = []

    st.session_state.tech_timings.append({
        "question": question,
        "time_taken_seconds": elapsed
    })

def get_total_time():
    if "tech_timings" not in st.session_state:
        return 0
    return round(sum(t["time_taken_seconds"] for t in st.session_state.tech_timings), 2)
