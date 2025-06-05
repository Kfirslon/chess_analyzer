import streamlit as st
from chess_analyzer import run_analysis

st.title("♟️ Kfir - Chess.com Game Analyzer")

username = st.text_input("Enter Chess.com username", value="kfirslon9")
year = st.number_input("Enter year", min_value=2000, max_value=2025, value=2025)
months_input = st.text_input(
    "Enter months (comma-separated, e.g., 1,2,3)", value="1,2,3,4,5"
)
clear_cache = st.checkbox("Clear country cache")

if st.button("Run Analysis"):
    try:
        months = [int(m.strip()) for m in months_input.split(",") if m.strip().isdigit()]
        df = run_analysis(username, year, months, clear_cache=clear_cache)
        st.success("Analysis complete!")
        st.dataframe(df.head())
    except Exception as e:
        st.error(f"Error: {e}")
