import os
import streamlit as st
import requests

BACKEND_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:8001")

st.title("DataMind v2 🧠")
st.write("Ask a question about the Brazilian e-commerce data.")

question = st.text_input(
    "Your question:",
    placeholder="e.g. Which product category made the most revenue?",
)

if st.button("Ask"):
    if question:
        with st.spinner("Thinking..."):
            response = requests.post(f"{BACKEND_URL}/ask", json={"question": question})
            answer = response.json()["answer"]
        st.markdown(answer)
    else:
        st.warning("Please enter a question.")