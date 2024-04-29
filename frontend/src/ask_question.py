import json
import streamlit as st
import requests
from utility import fetch_file_names_data


def ask_question(question, selected_file):
    try:
        url = "http://backend:8000/get_answer_by_chain"
        response = requests.post(
            url, json={"question": question, "filename": selected_file})
        if response.ok:
            json_data = response.json()
            answer = json.loads(json_data["data"])["answer"]
            st.success(json_data["message"])
            st.markdown(answer)
        elif response.status_code == 404:
            detail = response.json()["detail"]
            st.error(f"Something went wrong.")
            st.error(f"Deatils: {detail}")
        elif response.status_code == 500:
            st.error("Internal Server Error")
            st.error("Deatils:")
            st.error(response.json()["detail"])
        # if response.ok:
        return response
        # else:
        # return "Error: Unable to get answer"
    except Exception as e:
        return f"Error: {str(e)}"


def get_answer():
    st.title("Knowledge Summaries")
    st.write("Select the file")
    result = fetch_file_names_data("662c7428fb45c882e17567b8")
    selected_file = st.selectbox("Select file", result)
    if selected_file:
        st.title("Ask a Question")
        # Text input for the question
        question = st.text_input("Enter your question:")
        # Button to submit the question
        if st.button("Submit"):
            if question:
                response = ask_question(question, selected_file)

            else:
                st.error("Please enter a question.")
