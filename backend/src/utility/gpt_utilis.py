import re
import os
import logging
import openai
import pathlib
from pinecone import Pinecone
from backend.src.utility.pydantic_models import *
from PyPDF2 import PdfReader
from requests.exceptions import ConnectionError, Timeout
from retrying import retry
from backend.src.utility.file_utils import generate_filename_by_name
from backend.gpt.src.upsert_qa_to_pinecode import split_and_upsert, create_index
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from typing_extensions import Concatenate
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
from langchain.schema import Document

from dotenv import load_dotenv
# Load environment variables
load_dotenv()

# get root logger
# the __name__ resolve to "main" since we are at the root of the project.
logger = logging.getLogger(__name__)
# This will get the root logger since no logger in the configuration has this name.


MAX_RETRIES = 3
INITIAL_DELAY = 1
retry_config = {
    'stop_max_attempt_number': MAX_RETRIES,
    'wait_exponential_multiplier': INITIAL_DELAY * 1000,
    'wait_exponential_max': 10000,
    'retry_on_exception': lambda exc: isinstance(exc, (ConnectionError, Timeout))
}

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = "text-embedding-3-small"
pinecone_client = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))


def gen_markdown_from_question(question: Question) -> str:
    markdown_text = f"### {question.question}\n\n"
    markdown_text += "Options:\n\n"
    for option in question.options:
        markdown_text += f"- {option}\n"
    return markdown_text


def gen_markdown_from_question_answer(question_answer: QuestionAnswer) -> str:
    markdown_text = f"### {question_answer.question}\n\n"
    markdown_text += "Options:\n\n"
    for option in question_answer.options:
        markdown_text += f"- {option}\n"
    markdown_text += f"\n**Answer:** {question_answer.answer}\n\n"
    markdown_text += f"Justification: {question_answer.justification}\n\n"
    return markdown_text


def gen_markdown_from_Answer(answer: Answer) -> str:
    markdown_text = f"\n**Answer:** {answer.Answer}\n\n"
    markdown_text += f"Justification: {answer.Justification}\n\n"
    return markdown_text


@retry(**retry_config)
def chat_gpt_api_function(q_prompt):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system",
             "content": "You are a helpful answer bot designed to output JSON."},
            {"role": "user", "content": q_prompt}
        ]
    )
    return response


def get_gpt_response(q_prompt):
    try:
        response = chat_gpt_api_function(q_prompt)
        return response
    except Exception as e:
        logger.error(
            f"API call failed - Error occurred while getting GPT response: {e}")
        raise


def get_qa_from_json(topic_name, set='A'):
    try:
        qa_data = []
        file_name = generate_qa_filename(topic_name, "json", set)
        local_folder_path = f"/app/backend/src/json_files/"
        local_file_path = os.path.join(
            local_folder_path, os.path.basename(file_name))
        if os.path.exists(local_file_path):
            with open(local_file_path, "r") as file:
                qa_data = file.read()
            return qa_data
        else:
            raise FileNotFoundError(
                f"Summary data for topic '{topic_name}' not found.")
    except FileNotFoundError as e:
        logger.error(f"Error occurred while reading JSON file: {e}")
        raise
    except Exception as e:
        logger.error(f"Error occurred while reading JSON file: {e}")
        raise


def get_answer_by_summary_from_gpt(query, topic_name='Time-Series-Analysis'):
    try:
        namespace_name = f'doc-summary-{topic_name.replace(" ", "-")}'
        q_prompt = retrieve(query, namespace_name, 'cfa-articles-summary')
        response = get_gpt_response(q_prompt)
        summary_content = ""
        answer_instance: Answer()
        if response:
            summary_content = response.choices[0].message.content
            answer_instance = Answer.parse_raw(summary_content)
        return answer_instance
    except Exception as e:
        logger.error(f"Error occurred while getting summary from GPT: {e}")
        return None


def generate_filename(topic, filetype, separator='_', set='A'):
    clean_topic = re.sub(r'[^a-zA-Z0-9\s]', '', topic)
    filename = clean_topic.replace(' ', separator).lower(
    ) + f"_technical_qa_set{set}.{filetype}"
    return filename


def get_answer_by_gpt_vector_from_pc(query, topic_name='Time-Series-Analysis'):
    try:
        filename = generate_filename(topic_name, 'json', '_', 'B')
        namespace_name = filename.split(".")[0]
        q_prompt = retrieve(query, namespace_name, 'cfa-articles-qa')
        print(q_prompt)
        response = get_gpt_response(q_prompt)
        summary_content = ""
        answer_instance: Answer()  # type: ignore
        if response:
            summary_content = response.choices[0].message.content
            answer_instance = Answer.parse_raw(summary_content)
        return answer_instance
    except Exception as e:
        logger.error(f"Error occurred while getting summary from GPT: {e}")
        return None


def generate_qa_filename(topic, filetype, set='A'):
    clean_topic = re.sub(r'[^a-zA-Z0-9\s]', '', topic)
    filename = clean_topic.replace(' ', '_').lower(
    ) + f"_technical_qa_set{set}.{filetype}"
    return filename


def retrieve(query, namespace_name='doc-summary-Time-Series-Analysis', index_name='cfa-articles-summary'):
    limit = 3750
    index = pinecone_client.Index(index_name)
    res = client.embeddings.create(input=query, model=MODEL)

    xq = res.data[0].embedding

    match_res = index.query(
        vector=[xq], top_k=5, namespace=namespace_name, include_metadata=True)
    contexts = [
        x['metadata']['text'] for x in match_res['matches']
    ]

    prompt_start = (
        """Answer the question based on the context below along with brief justifications.
        Please ensure that each answer is accompanied by a brief explanation, starting with "Answer:" followed by the correct option and "with justification - " followed by the rationale supporting the answer.
        Example:
        Answer: C with Justification - Paris is the capital of France, known for its iconic landmarks like the Eiffel Tower.
        \n\n Context start:\n"""
    )
    prompt_end = (
        f"\n\n Context end\n\nQuestion: {query}\nAnswer:"
    )

    prompt = prompt_start

    for i, context in enumerate(contexts):
        if len(prompt) + len(context) + len(prompt_end) >= limit:
            break
        else:
            prompt += "\n\n---\n\n" + context

    prompt += prompt_end

    return prompt


def retrieve_conext(query, index_name, namespace_name=''):
    #     limit = 3750
    index = pinecone_client.Index(index_name)
    res = client.embeddings.create(input=query, model=MODEL)

    xq = res.data[0].embedding

    match_res = index.query(
        vector=[xq], top_k=5, namespace=namespace_name, include_metadata=True)
    contexts = [
        x['metadata']['text'] for x in match_res['matches']
    ]

    return contexts


def get_content_from_file(file_location):
    if file_location:
        # provide the path of  pdf file/files.
        pdfreader = PdfReader(str(file_location))
        # read text from pdf
        raw_text = ''
        for i, page in enumerate(pdfreader.pages):
            content = page.extract_text()
            if content:
                raw_text += content
        return raw_text
    else:
        return None


def upsert_file_content(index_name, file_location, namespace):
    try:
        content = get_content_from_file(file_location)
        if content:
            split_and_upsert(index_name, content, namespace)
    except Exception as e:
        print(str(e))


def get_chain_run_result(query, index_name, filename):
    try:
        docs = []
        namespace_name = generate_filename_by_name(filename)

        print(pinecone_client.list_indexes().names())
        print(index_name in pinecone_client.list_indexes().names())
        if index_name not in pinecone_client.list_indexes().names():
            index = pinecone_client.Index(index_name)
        else:
            create_index(index_name)
            index = pinecone_client.Index(index_name)
        print(index)
        namespace_list = list(index.describe_index_stats()[
                              "namespaces"].keys())
        print(namespace_list)
        print(namespace_name)
        print(namespace_name in namespace_list)
        if len(namespace_list):
            if namespace_name in namespace_list:
                context = retrieve_conext(query, index_name, namespace_name)
                for text in context:
                    doc = Document(page_content=text)
                    docs.append(doc)
                chain = load_qa_chain(OpenAI(), chain_type="stuff")
                response_msg = chain.run(input_documents=docs, question=query)
                response = {"code": 200, "answer": response_msg}

            else:
                response = {
                    "code": 404, "answer": "Knowledge base not found. Please try training again!"}
        else:
            response = {
                "code": 404, "answer": "Knowledge base not found. Please try training again!"}
        return response
    except Exception as e:
        print(str(e))
        return {"code": 500, "answer": "Something went wrong. Please try again!"}
