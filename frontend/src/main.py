import json
import streamlit as st
import warnings
from utility import *
from os import path
import pandas as pd
import plotly.express as px
from streamlit.logger import get_logger
from summarization import summarize
from ask_question import get_answer
warnings.filterwarnings("ignore")

logger = get_logger(__name__)


# Define navigation pane
st.sidebar.title("Navigation")


# Page 1 definition
def knowledge_summary():
    st.title("Knowledge Summary")
    st.write("Select the topic")
    selected_topic = st.selectbox("Select topic", [
        "Time-Series Analysis",
        "Machine Learning",
        "Organizing, Visualizing, and Describing Data"
    ])
    summary = fetch_summary_data(selected_topic)
    if summary:
        st.write(f"{selected_topic} summary:")
        st.write(summary)
    else:
        st.write("Error fetching summary data.")


# Page 2 definition
def summaries_for_files():
    st.title("Knowledge Summaries")
    st.write("Select the file")
    result = fetch_file_names_data("662c7428fb45c882e17567b8")
    selected_file = st.selectbox("Select topic", result)
    if st.button('Get Summary (click once and wait)'):
        summary = fetch_summary_data("662c7428fb45c882e17567b8", selected_file)
        st.markdown(summary, unsafe_allow_html=True)
    # selected_set = st.selectbox("Select Set", ["A", "B"])
    # qa_data = fetch_qa_data(selected_topic)
    # questions = [entry["question"] for entry in qa_data]
    # selected_question = st.selectbox("Select a question", questions)
    # question = next(
    #     (entry for entry in qa_data if entry["question"] == selected_question), None)
    # if question:
    #     markdown_text = display_question(question)
    #     st.markdown(markdown_text)


def ask_question():
    get_answer()

# Page 2 definition


def Knowledge_base_QA():
    st.title("Knowledge base Q/A")
    st.write("Select the topic")
    selected_topic = st.selectbox("Select topic", [
        "Time-Series Analysis",
        "Machine Learning",
        "Organizing, Visualizing, and Describing Data"
    ])
    selected_set = st.selectbox("Select Set", ["A", "B"])
    qa_data = fetch_qa_data(selected_topic, selected_set)
    questions = [entry["question"] for entry in qa_data]
    selected_question = st.selectbox("Select a question", questions)
    question = next(
        (entry for entry in qa_data if entry["question"] == selected_question), None)
    if question:
        markdown_text = display_question(question)
        st.markdown(markdown_text)


# Page 3 definition
def Answer_by_qa_vector():
    st.title("Find answer by vector database")
    st.write("Select the topic")
    selected_topic = st.selectbox("Select topic", [
        "Time-Series Analysis",
        "Machine Learning",
        "Organizing, Visualizing, and Describing Data"
    ])
    selected_set = st.selectbox("Select Set", ["A", "B"])
    qa_data = fetch_qa_data(selected_topic, selected_set)
    questions = [entry["question"] for entry in qa_data]
    selected_question = st.selectbox("Select a question", questions)
    question = next(
        (entry for entry in qa_data if entry["question"] == selected_question), None)

    if question:
        markdown_text = display_question(question)
        st.markdown(markdown_text)

        # Add a button to get answer by RAG methodology
        if st.button("Get Answer by RAG methodology"):
            try:
                question_entry = [
                    entry for entry in qa_data if entry["question"] == selected_question][0]
                data_dict = json.dumps(question_entry)
                answer = fetch_answer_by_gpt_with_pc_qa_context(
                    data_dict, selected_topic)
                st.write("Answer by RAG methodology:")
                if answer:
                    st.markdown(answer)
                else:
                    st.write("Error")
            except Exception as e:
                logger.error(
                    f"Error getting answer by RAG methodology: {str(e)}")


# Page 4 definition
def Answer_by_summary_vectors():
    st.title("Find answer by knowledge summary")
    st.write("Select the topic")
    selected_topic = st.selectbox("Select topic", [
        "Time-Series Analysis",
        "Machine Learning",
        "Organizing, Visualizing, and Describing Data"
    ])
    selected_set = st.selectbox("Select Set", ["A", "B"])
    qa_data = fetch_qa_data(selected_topic, selected_set)
    questions = [entry["question"] for entry in qa_data]
    selected_question = st.selectbox("Select a question", questions)
    question = next(
        (entry for entry in qa_data if entry["question"] == selected_question), None)

    if question:
        markdown_text = display_question(question)
        st.markdown(markdown_text)

    # Add a button to get answer by RAG methodology
    if st.button("Get Answer by RAG methodology"):
        try:
            question_entry = [
                entry for entry in qa_data if entry["question"] == selected_question][0]
            data_dict = json.dumps(question_entry)
            answer = fetch_answer_by_gpt_with_pc_summary_context(
                data_dict, selected_topic)
            st.write("Answer by RAG methodology:")
            if answer:
                st.markdown(answer)
            else:
                st.write("Error")
        except Exception as e:
            logger.error(f"Error getting answer by RAG methodology: {str(e)}")


def answer_stats_qa_based():
    answer_stats(baesd="qa_based")


def answer_stats_summary_based():
    answer_stats(baesd="summary_based")


def answer_stats(baesd="qa_based"):
    st.title("Knowledge Base Answer Statistics")

    answer_stats_qa_based = fetch_answer_stats(baesd)

    if answer_stats_qa_based is not None:
        df = pd.DataFrame({"Category": ["Correct", "Wrong"], "Count": [
                          answer_stats_qa_based["correct_answers"], answer_stats_qa_based["wrong_answers"]]})

        fig = px.bar(df, x="Category", y="Count", color="Category", title="Answer Distribution",
                     color_discrete_map={"Correct": "green", "Wrong": "red"})
        st.plotly_chart(fig)

        st.metric("Total Answers", answer_stats_qa_based["total_answers"])
    else:
        st.write("Failed to retrieve data.")

    answer_stats_summary_based = fetch_answer_stats(baesd)


def home_page():
    pages = {
        "Knowledge summary": summarize,
        "Knowledge Summaries for files": summaries_for_files,
        "Ask Question": ask_question,
        # "Knowledge base Q/A": Knowledge_base_QA,
        # "Find answer by vector database": Answer_by_qa_vector,
        # "Find answer by knowledge summary": Answer_by_summary_vectors,
        # "Knowledge Base Performance QA Based": answer_stats_qa_based,
        # "Knowledge Base Performance Summary Based": answer_stats_summary_based
    }
    st.markdown(
        """
        <style>
            .sidebar .sidebar-content {
                padding-top: 2rem;
                padding-bottom: 10rem;
                padding-left: 1rem;
                padding-right: 1rem;
            }
            .stTabs > div[role="tablist"] > .stTab {
                flex: 1;
            }
            .stTabs > div[role="tablist"] {
                display: flex;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # selected_page = st.sidebar.selectbox("Select Page", list(pages.keys()))
    selected_page = st.sidebar.radio("", list(pages.keys()))
    if selected_page:
        pages[selected_page]()


if __name__ == "__main__":
    home_page()
