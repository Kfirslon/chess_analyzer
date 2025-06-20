import streamlit as st
from chess_analyzer import run_analysis

st.markdown(
    """
    <style>
        .top-left {
            position: fixed;
            top: 12px;
            left: 12px;
            font-size: 14px;
            color: gray;
            background-color: rgba(255, 255, 255, 0.7);
            padding: 4px 8px;
            border-radius: 6px;
            z-index: 1000;
        }
    </style>
    <div class="top-left">🔹 by Kfir Slonimski</div>
    """,
    unsafe_allow_html=True
)

st.title("♟️ Kfir - Chess.com Game Analyzer")

username = st.text_input("Enter Chess.com username", value="username")
year = st.number_input("Enter year", min_value=2000, max_value=2025, value=2025)
months_input = st.text_input("Enter months (comma-separated, e.g., 1,2,3)", value="1")

if st.button("Run Analysis"):
    try:
        months = [int(m.strip()) for m in months_input.split(",") if m.strip().isdigit()]
        run_analysis(username, year, months)
    except Exception as e:
        st.error(f"Error: {e}")
