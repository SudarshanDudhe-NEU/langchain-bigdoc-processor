import streamlit as st
import requests


def summarize():
    url = "http://backend:8000/"
    """
    The main function for the Streamlit app.

    :return: None.
    """
    st.title("Document Summarizer")


    # if input_method == 'Upload a document':
    uploaded_file = st.file_uploader(
        "Upload a document to summarize, 10k to 100k tokens works best!", type=['txt', 'pdf'])

    if uploaded_file:
        if st.button('Summarize (click once and wait)'):
            # files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
            st.session_state["resume_file_name"] = uploaded_file.name
            print("file name is", uploaded_file.name)
            files = {"file": (uploaded_file.name,
                                uploaded_file.getvalue())}
            response = requests.post(f"{url}upload", files=files)
            if response.status_code == 200:
                st.markdown(response.json()[
                            "summary"], unsafe_allow_html=True)
   