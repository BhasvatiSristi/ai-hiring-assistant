import streamlit as st

def load_styles():
    st.markdown("""
    <style>

    .stApp {
        background: #f7f9fc;
        opacity:0.5;
    }

    [data-testid="stChatMessage"] {
        background: white;
        
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 10px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }

    textarea {
        border-radius: 10px !important;
    }

    h1 {
        color: #1f3a8a;
    }

    </style>
    """, unsafe_allow_html=True)

