import streamlit as st
import logging
logging.getLogger("streamlit.watcher.local_sources_watcher").setLevel(logging.ERROR)
from agent import run_agent
from tools.pdf_reader import read_pdf
from tools.chunker import chunk_text
from tools.embeddings import create_embeddings
from tools.vector_store import create_index, search_index
from auth.auth import login_user
from auth.auth import register_user
from auth.db import create_database
create_database()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "page" not in st.session_state:
    st.session_state.page = "login"

if not st.session_state.logged_in:

    if st.session_state.page == "login":

        st.title("Login")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login"):
            if login_user(username, password):
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Invalid credentials")

        # Sign Up button on login page
        if st.button("Sign Up"):
            st.session_state.page = "signup"
            st.rerun()

    elif st.session_state.page == "signup":

        st.title("Sign Up")
        reg_username = st.text_input("Username", key="reg_username")
        reg_password = st.text_input("Password", type="password", key="reg_password")

        if st.button("Sign Up"):
            if register_user(reg_username, reg_password):
                st.success("Registered successfully. Please log in.")
                # st.session_state.page = "login"
                st.rerun()
            else:
                st.error("Username already taken.")

        # Back to Login button
        if st.button("Back to Login"):
            st.session_state.page = "login"
            st.rerun()

def show_agent():

    with st.sidebar:

        st.header("Controls")

        if st.button("Logout"):

            st.session_state.logged_in = False
            st.session_state.page = "login"
            st.rerun()

        if st.button("Clear Chat"):

            st.session_state.messages = []

            if "pdf_text" in st.session_state:
                del st.session_state.pdf_text

            if "pdf_summary" in st.session_state:
                del st.session_state.pdf_summary

            st.rerun()

        uploaded_file = st.file_uploader("Upload PDF",type=["pdf"])

        if uploaded_file and "index" not in st.session_state:

            st.success(f"Uploaded: {uploaded_file.name}")
            pdf_text = read_pdf(uploaded_file)
            st.session_state.pdf_text = pdf_text
            chunks = chunk_text(pdf_text)

            # print(f"Total Chunks: {len(chunks)}")
            embeddings = create_embeddings(chunks)

            # print(embeddings.shape)
            index = create_index(embeddings)

            st.session_state.index = index
            st.session_state.chunks = chunks
    

    st.title("AI ChatBot")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:

        with st.chat_message(message["role"]):

            st.markdown(message["content"])

    # if uploaded_file and "pdf_summary" not in st.session_state:
    #     summary = run_agent(
    #         f"Summarize this document:\n\n{pdf_text}"
    #     )
    #     with st.chat_message("assistant"):
    #          st.markdown(summary)

    #     st.session_state.pdf_summary = summary

    #     st.session_state.messages.append({
    #         "role": "assistant",
    #         "content": summary
    #     })

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

            question_embedding = create_embeddings(
            [prompt]
        )

            retrieved_chunks = search_index(
            question_embedding,
            st.session_state.index,
            st.session_state.chunks
            )

            context = "\n".join(retrieved_chunks)

            response = run_agent(
                f"""

    Use the context below to answer the question.

    Context:

    {context}

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

if st.session_state.logged_in:

    show_agent()