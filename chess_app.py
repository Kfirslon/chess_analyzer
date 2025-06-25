import streamlit as st
from chess_analyzer import run_analysis

st.markdown(
    """
    <style>
        /* Background */
        .stApp {
            background: linear-gradient(135deg, #2d402d, #6f8d6f);
            color: #f0f0f0;
        }

        /* Top-left credit */
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

        /* Labels */
        label, .stTextInput label, .stNumberInput label {
            color: white !important;
            font-weight: bold;
        }

        /* Placeholder text */
        input::placeholder {
            color: #cccccc !important;
            opacity: 1 !important;
        }

        /* Input fields */
        input, .stNumberInput input, .stTextInput > div > div > input {
            background-color: #ffffff !important;
            color: #000000 !important;
            border: 1px solid #333 !important;
            border-radius: 6px !important;
        }

        /* Style only the Run Analysis button */
        div.stButton > button {
            background-color: #f44336 !important;
            color: white !important;
            font-weight: bold;
            border: none !important;
            border-radius: 10px !important;
            padding: 0.5rem 1.2rem !important;
        }

        /* Hide Streamlit toolbar and menu */
        [data-testid="stToolbar"],
        [data-testid="stDeployButton"],
        [data-testid="stSidebarNav"],
        header, footer {
            visibility: hidden !important;
            height: 0 !important;
            position: fixed !important;
        }

        /* Hide “Manage app” button in bottom right */
        div[data-testid="stActionButtonIcon"] {
            display: none !important;
        }

        /* Spinner/info text */
        [data-testid="stMarkdownContainer"] p {
            color: white !important;
            font-weight: bold;
        }

        /* Error message */
        [data-testid="stNotificationContentError"] {
            color: #ffdddd !important;
            font-weight: bold;
        }

        /* Success message */
        [data-testid="stNotificationContentSuccess"] {
            color: #d4ffd4 !important;
            font-weight: bold;
        }

        /* Hide chain link icon in headers */
        h1 > a, h2 > a, h3 > a {
            display: none !important;
        }
    </style>

    <div class="top-left">♟️ by Kfir Slonimski</div>
    """,
    unsafe_allow_html=True
)



st.title("♟️ HaTaktikan - Chess Analyzer")

username = st.text_input("Enter Chess.com username", value="drchessbot")
year = st.number_input("Enter year", min_value=2000, max_value=2025, value=2025)
months_input = st.text_input("Enter months (comma-separated, e.g., 1,2,3)", value="1")

if st.button("Run Analysis"):
    try:
        months = [int(m.strip()) for m in months_input.split(",") if m.strip().isdigit()]
        
        with st.spinner("⏳ Analyzing your games..."):
            run_analysis(username, year, months)

        st.success("✅ Analysis complete!")
    except Exception as e:
        st.error(f"❌ Error: {e}")
