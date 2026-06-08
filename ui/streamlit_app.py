import streamlit as st
import logging
logging.getLogger("streamlit.watcher.local_sources_watcher").setLevel(logging.ERROR)
from agent import run_agent
from tools.pdf_reader import read_pdf
from tools.chunker import chunk_text
from tools.embeddings import create_embeddings
from tools.vector_store import create_index, search_index

with st.sidebar:

    st.header("Controls")

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