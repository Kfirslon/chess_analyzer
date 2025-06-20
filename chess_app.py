import streamlit as st
from chess_analyzer import run_analysis

st.markdown(
    """
    <style>
        /* Background with a chess-like vibe */
        .stApp {
            background: radial-gradient(circle at top left, #d2b48c, #8b5e3c);
            color: #222;
        }

        /* Top-left credit */
        .top-left {
            position: fixed;
            top: 12px;
            left: 12px;
            font-size: 14px;
            color: #333;
            background-color: rgba(255, 255, 255, 0.9);
            padding: 4px 10px;
            border-radius: 6px;
            z-index: 1000;
            box-shadow: 0 0 5px rgba(0,0,0,0.1);
        }

        /* Input field visibility fix */
        input, .stNumberInput, .stTextInput > div > div > input {
            background-color: #fdfdfd !important;
            color: #111 !important;
        }

        /* Button style */
        button {
            background-color: #444444 !important;
            color: white !important;
            border-radius: 6px !important;
        }
    </style>
    <div class="top-left">🔹 by Kfir Slonimski</div>
    """,
    unsafe_allow_html=True
)

st.title("♟️ Chess.com Game Analyzer")

username = st.text_input("Enter Chess.com username", value="username")
year = st.number_input("Enter year", min_value=2000, max_value=2025, value=2025)
months_input = st.text_input("Enter months (comma-separated, e.g., 1,2,3)", value="1")

if st.button("Run Analysis"):
    try:
        months = [int(m.strip()) for m in months_input.split(",") if m.strip().isdigit()]
        run_analysis(username, year, months)
    except Exception as e:
        st.error(f"Error: {e}")
