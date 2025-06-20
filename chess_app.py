import streamlit as st
from chess_analyzer import run_analysis

st.markdown(
    """
    <style>
        .stApp {
            background: linear-gradient(135deg, #2d402d, #6f8d6f);
            color: #f0f0f0;
        }

        .top-left {
            position: fixed;
            top: 12px;
            left: 12px;
            font-size: 14px;
            color: white;
            background-color: rgba(0, 0, 0, 0.6);
            padding: 5px 10px;
            border-radius: 6px;
            z-index: 1000;
        }

        label, .stTextInput label, .stNumberInput label {
            color: white !important;
        }

        input, .stNumberInput input, .stTextInput > div > div > input {
            background-color: #ffffff !important;
            color: #000000 !important;
            border: 1px solid #333 !important;
            border-radius: 6px !important;
        }

        button {
            background-color: #ffffff !important;
            color: #2d402d !important;
            border-radius: 6px !important;
            border: 1px solid #2d402d !important;
            font-weight: bold;
        }

        /* FULLY hide Streamlit's top-right controls (GitHub, Share, Edit, Menu, Feedback) */
        [data-testid="stToolbar"],
        [data-testid="stDeployButton"],
        [data-testid="stSidebarNav"],
        header, footer {
            visibility: hidden !important;
            height: 0 !important;
            position: fixed !important;
        }

        /* Hide 'Manage app' button at bottom-right */
        div[data-testid="stActionButtonIcon"] {
            display: none !important;
        }
    </style>

    <div class="top-left">♟️ by Kfir Slonimski</div>
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
