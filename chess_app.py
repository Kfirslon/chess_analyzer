# chess_app.py
import streamlit as st
from chess_analyzer import analyze_chess_games_in_folder, download_monthly_games, render_all_graphs

st.title("♟️ Kfir - Chess.com Game Analyzer")

USERNAME = st.text_input("Enter Chess.com username", value="kfirslon9")
YEAR = st.number_input("Enter year", min_value=2000, max_value=2025, value=2025)
months_input = st.text_input("Enter months (comma-separated, e.g., 1,2,3)", value="1,2,3")

if st.button("Run Analysis"):
    try:
        months = [int(m.strip()) for m in months_input.split(",") if m.strip().isdigit()]
        folder = f"chess_games/{USERNAME.lower()}"
        download_monthly_games(USERNAME, YEAR, months, folder)
        df = analyze_chess_games_in_folder(folder, USERNAME)
        df = df.sort_values("datetime")
        df["month"] = df["datetime"].dt.strftime("%B")
        render_all_graphs(df)
    except Exception as e:
        st.error(f"Error: {e}")
