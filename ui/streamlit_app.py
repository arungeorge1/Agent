import streamlit as st
from agent import run_agent
from tools.pdf_reader import read_pdf

with st.sidebar:

    st.header("Controls")

    if st.button("Clear Chat"):

        st.session_state.messages = []
        if "pdf_summary" in st.session_state:
            del st.session_state.pdf_summary

        if "pdf_text" in st.session_state:
            del st.session_state.pdf_text

        st.rerun()

    uploaded_file = st.file_uploader("Upload PDF",type=["pdf"])

    if uploaded_file:

        st.success(f"Uploaded: {uploaded_file.name}")
        pdf_text = read_pdf(uploaded_file)
        st.session_state.pdf_text = pdf_text
   

st.title("AI ChatBot")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

if uploaded_file and "pdf_summary" not in st.session_state:
    summary = run_agent(
        f"Summarize this document:\n\n{pdf_text}"
    )
    with st.chat_message("assistant"):
         st.markdown(summary)

    st.session_state.pdf_summary = summary

    st.session_state.messages.append({
        "role": "assistant",
        "content": summary
    })

# if "pdf_summary" in st.session_state:
#     st.markdown(st.session_state.pdf_summary)

prompt = st.chat_input("Ask something")

if prompt:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    if "pdf_text" in st.session_state:

        response = run_agent(
            f"""
Document:

{st.session_state.pdf_text}

Question:

{prompt}
"""
        )

    else:

        response = run_agent(prompt)

    with st.chat_message("assistant"):
        st.markdown(response)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response
        }
    )