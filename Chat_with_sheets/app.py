import streamlit as st
import pandas as pd
from granite_chat_model import (
    read_excel_summary,
    generate_prompt_from_df,
    chat_with_model
)
import os, base64

st.set_page_config(layout="wide", page_title="Granite Chat Assistant")

# --- Custom CSS ---
st.markdown("""
<style>
.sidebar-title {
    font-size: 1.2rem;
    font-weight: 700;
    margin-bottom: 10px;
}
.chat-bubble.user {
    background-color: #e0f7fa;
    padding: 1em;
    border-radius: 10px;
    margin: 1em 0;
    font-weight: 600;
}
.chat-bubble.bot {
    background-color: #f1f3f4;
    padding: 1em;
    border-radius: 10px;
    margin-bottom: 1em;
}
.logo-circle {
    display: block;
    margin-left: auto;
    margin-right: auto;
    border-radius: 50%;
    width: 120px;
    height: 120px;
    object-fit: cover;
    box-shadow: 0 2px 12px rgba(0,0,0,0.08);
    border: 3px solid #f0f2f6;
    margin-bottom: 1em;
}
</style>
""", unsafe_allow_html=True)

# --- Sidebar: Logo & Upload ---
with st.sidebar:
    st.markdown("### Granite Chat 💬")

    logo_path = "symbol.jpg"
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode()
            ext = os.path.splitext(logo_path)[1].lower()
            mime = "png" if ext == ".png" else "jpeg"
            st.markdown(
                f'<img src="data:image/{mime};base64,{encoded}" class="logo-circle">',
                unsafe_allow_html=True
            )

    st.markdown('<div class="sidebar-title">Upload Excel File</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Choose .xlsx file", type=["xlsx"])

# --- Load and Preview Excel ---
df = None
if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        st.success("✅ File loaded successfully.")
        st.dataframe(df.head(10), use_container_width=True)
    except Exception as e:
        st.error(f"❌ Error reading file: {e}")

# --- Initialize Chat State ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Function to Extract Summary ---
def extract_structured_summary(text):
    lines = []
    keywords = [
        "Sample ID", "Patient Name", "Test Type", "Date",
        "Screening", "Mutation", "Result", "Diagnosis"
    ]
    for key in keywords:
        if key.lower() in text.lower():
            for sentence in text.split("."):
                if key.lower() in sentence.lower():
                    lines.append(f"**{key}:** {sentence.strip()}")
                    break
    if not lines:
        return "*No structured summary could be extracted.*"
    return "\n".join(lines)

# --- Main Chat UI ---
st.title("📊 Granite Chat Assistant")
st.write("Ask questions based on the uploaded Excel sheet.")

if df is not None:
    for entry in st.session_state.chat_history:
        st.markdown(f'<div class="chat-bubble user">🧑‍💼 You: {entry["question"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="chat-bubble bot">🤖 <b>Summary:</b><br>{entry["summary"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="chat-bubble bot"><b>Full Answer:</b><br>{entry["answer"]}</div>', unsafe_allow_html=True)

    question = st.chat_input("Type your question here...")
    if question:
        with st.spinner("Generating response..."):
            prompt = generate_prompt_from_df(df, question)
            try:
                response = chat_with_model(prompt)
            except Exception as e:
                response = f"Error: {str(e)}"

            structured_summary = extract_structured_summary(response)

            st.session_state.chat_history.append({
                "question": question,
                "answer": response,
                "summary": structured_summary
            })

        st.rerun()

else:
    st.info("📤 Please upload an Excel file to start chatting.")


