import streamlit as st

from backend.src.utility.summariztion_utils import (
    doc_loader, summary_prompt_creator, doc_to_final_summary,
)
from backend.src.utility.my_prompts import file_map, file_combine, youtube_map, youtube_combine
from backend.src.utility.text_utils import check_gpt_4, check_key_validity, create_temp_file, create_chat_model, \
    token_limit, token_minimum


def process_summarize_button(file_or_transcript, api_key, use_gpt_4, find_clusters, file=True):
    """
    Processes the summarize button, and displays the summary if input and doc size are valid

    :param file_or_transcript: The file uploaded by the user or the transcript from the YouTube URL

    :param api_key: The API key entered by the user

    :param use_gpt_4: Whether to use GPT-4 or not

    :param find_clusters: Whether to find optimal clusters or not, experimental

    :return: None
    """
    try:
        # print(file_or_transcript)
        # if not validate_input(file_or_transcript, api_key, use_gpt_4):
        #     return

        # with st.spinner("Summarizing... please wait..."):
        if file_or_transcript:
            temp_file_path = create_temp_file(file_or_transcript)
            print(temp_file_path)
            doc = doc_loader(temp_file_path)
            map_prompt = file_map
            combine_prompt = file_combine
        else:
            doc = file_or_transcript
            map_prompt = youtube_map
            combine_prompt = youtube_combine

        llm = create_chat_model(api_key, use_gpt_4)
        initial_prompt_list = summary_prompt_creator(map_prompt, 'text', llm)
        final_prompt_list = summary_prompt_creator(combine_prompt, 'text', llm)
        if not validate_doc_size(doc)["result"]:
            if file:
                pass
                # os.unlink(temp_file_path)
            return

        if find_clusters:
            summary = doc_to_final_summary(
                doc, 10, initial_prompt_list, final_prompt_list, api_key, use_gpt_4, find_clusters)

        else:
            summary = doc_to_final_summary(
                doc, 10, initial_prompt_list, final_prompt_list, api_key, use_gpt_4)

        # st.markdown(summary, unsafe_allow_html=True)
        if file:
            pass
            # os.unlink(temp_file_path)
        return summary
    except Exception as e:
        print(str(e))


def validate_doc_size(doc):
    """
    Validates the size of the document

    :param doc: doc to validate

    :return: True if the doc is valid, False otherwise
    """
    if not token_limit(doc, 800000):
        # st.warning('File or transcript too big!')
        return {"result": False, "msg": 'File or transcript too big!'}

    if not token_minimum(doc, 2000):
        # st.warning('File or transcript too small!')
        return {"result": False, "msg": 'File or transcript too small!'}
    return {"result": True, "msg": 'Success'}


def validate_input(file_or_transcript, api_key, use_gpt_4):
    """
    Validates the user input, and displays warnings if the input is invalid

    :param file_or_transcript: The file uploaded by the user or the YouTube URL entered by the user

    :param api_key: The API key entered by the user

    :param use_gpt_4: Whether the user wants to use GPT-4

    :return: True if the input is valid, False otherwise
    """
    if file_or_transcript == None:
        st.warning("Please upload a file or enter a YouTube URL.")
        return False

    if not check_key_validity(api_key):
        st.warning('Key not valid or API is down.')
        return False

    if use_gpt_4 and not check_gpt_4(api_key):
        st.warning('Key not valid for GPT-4.')
        return False

    return True
