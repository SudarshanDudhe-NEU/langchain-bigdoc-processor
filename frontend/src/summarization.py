import streamlit as st
import requests


def summarize():
    url = "http://backend:8000/"
    """
    The main function for the Streamlit app.

    :return: None.
    """
    st.title("Document Summarizer")

    input_method = st.radio("Select input method",
                            ('Upload a document'))

    if input_method == 'Upload a document':
        uploaded_file = st.file_uploader(
            "Upload a document to summarize, 10k to 100k tokens works best!", type=['txt', 'pdf'])
        print(uploaded_file)

    # if input_method == 'Enter a YouTube URL':
    #     youtube_url = st.text_input("Enter a YouTube URL to summarize")

    # api_key = st.text_input(
    #     "Enter API key here, or contact the author if you don't have one.")
    # st.markdown('[Author email](mailto:ethanujohnston@gmail.com)')
    # use_gpt_4 = st.checkbox(
    #     "Use GPT-4 for the final prompt (STRONGLY recommended, requires GPT-4 API access - progress bar will appear to get stuck as GPT-4 is slow)", value=True)
    # find_clusters = st.checkbox(
    #     'Find optimal clusters (experimental, could save on token usage)', value=False)
    # st.sidebar.markdown('# Made by: [Ethan](https://github.com/e-johnstonn)')
    # st.sidebar.markdown(
    #     '# Git link: [Docsummarizer](https://github.com/e-johnstonn/docsummarizer)')
    # st.sidebar.markdown("""<small>It's always good practice to verify that a website is safe before giving it your API key.
    #                     This site is open source, so you can check the code yourself, or run the streamlit app locally.</small>""", unsafe_allow_html=True)
    if input_method == 'Upload a document':
        if uploaded_file:
            if st.button('Summarize (click once and wait)'):
                # files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                st.session_state["resume_file_name"] = uploaded_file.name
                print("file name is", uploaded_file.name)
                files = {"file": (uploaded_file.name,
                                  uploaded_file.getvalue())}
                response = requests.post(f"{url}upload", files=files)
                if response.status_code == 200:
                    st.markdown(response.json()["summary"],unsafe_allow_html=True)
    else:
        pass
        # doc = transcript_loader(youtube_url)
        # summary = process_summarize_button(
        #     doc, api_key, use_gpt_4, find_clusters, file=False)
        # st.markdown(summary, unsafe_allow_html=True)

