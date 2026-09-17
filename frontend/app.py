import os
import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

BACKEND_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:8001")

st.title("DataMind v2 🧠")
st.write("Ask a question about the Brazilian e-commerce data.")

question = st.text_input(
    "Your question:",
    placeholder="e.g. Show me a bar chart of revenue by category",
)

if st.button("Ask"):
    if question:
        with st.spinner("Thinking..."):
            response = requests.post(f"{BACKEND_URL}/ask", json={"question": question})
            data = response.json()

        st.markdown(data["answer"])              # show the text answer

        chart = data.get("chart")                # draw the chart if there is one
        if chart:
            labels = chart["labels"]
            values = chart["values"]
            chart_type = chart.get("chart_type", "bar")

            if chart_type == "pie":
                fig, ax = plt.subplots()
                ax.pie(values, labels=labels, autopct="%1.1f%%")
                st.pyplot(fig)
            else:
                df = pd.DataFrame({"value": values}, index=labels)
                if chart_type == "line":
                    st.line_chart(df)
                else:
                    st.bar_chart(df)
    else:
        st.warning("Please enter a question.")