import json
import requests
from streamlit.logger import get_logger


logger = get_logger(__name__)


def fetch_summary_data(topic):
    try:
        response = requests.get(
            f"http://backend:8000/get_summary_data/{topic}")
        response.raise_for_status()
        return response.json().get("data", "")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching summary data: {e}")
        raise Exception(f"Error fetching summary data: {e}")


def fetch_qa_data(topic, set_id):
    try:
        logger.info(f"fetching QA data:")
        response = requests.get(
            f"http://backend:8000/get_qa_data/{topic}/{set_id}")
        response.raise_for_status()
        return json.loads(response.json().get("data", "[]"))
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching QA data: {e}")
        raise Exception(f"Error fetching QA data: {e}")


def fetch_file_names_data(user_id):
    try:
        logger.info(f"fetching QA data:")
        response = requests.get(
            f"http://backend:8000/get_file_names_data/{user_id}/")
        return response.json().get("data", [])
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching QA data: {e}")
        raise Exception(f"Error fetching QA data: {e}")


def fetch_summary_data(user_id, selected_file):
    try:
        logger.info(f"fetching QA data:")
        response = requests.get(
            f"http://backend:8000/get_file_summary_data/{user_id}/{selected_file}")
        return response.json().get("data", [])
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching QA data: {e}")
        raise Exception(f"Error fetching QA data: {e}")


def fetch_answer_by_gpt_with_pc_summary_context(jsondump, selected_topic):
    question_dict = json.loads(jsondump)

    data = {"topic": selected_topic, "question": question_dict}
    url = f"http://backend:8000/get_answer_by_gpt_with_pc_summary_context"
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        if response.status_code == 200:
            return response.json().get("markdown_text", {})
        else:
            return None
    except Exception as e:
        logger.error(
            f"Error fetching answer by GPT with PC summary context: {e}")
        raise Exception(
            f"Error fetching answer by GPT with PC summary context: {e}")


def fetch_answer_by_gpt_with_pc_qa_context(jsondump, selected_topic):
    question_dict = json.loads(jsondump)

    data = {"topic": selected_topic, "question": question_dict}
    url = f"http://backend:8000/get_answer_by_gpt_with_pc_qa_context"
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        if response.status_code == 200:
            return response.json().get("markdown_text", {})
        else:
            return None
    except Exception as e:
        logger.error(f"Error fetching answer by GPT with PC QA context: {e}")
        raise Exception(
            f"Error fetching answer by GPT with PC QA context: {e}")


def display_question(question):
    markdown_lines = [
        f"### {question['question']}",
        "Options:",
        *[f"{option}\n\n" for option in question['options']],
        f"**Answer:** {question['answer']}\n\n",
        f"Justification: {question['justification']}"
    ]
    markdown_text = "\n".join(markdown_lines)
    return markdown_text


def fetch_answer_stats(based="qa_based"):
    try:
        print("here")
        response = requests.get(f"http://backend:8000/answer_stats/{based}")
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None
