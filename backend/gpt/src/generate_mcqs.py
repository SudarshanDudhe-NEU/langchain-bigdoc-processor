import sys
import csv
import os
import re
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def read_text_from_csv(file_path, title_column_name, column_name, title_value):
    texts = []
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row[title_column_name] == title_value:
                texts.append(row[column_name])
    return texts[0]


def get_learning_outcome_and_summary_text(title_value='Time-Series Analysis'):
    result = []
    try:
        file_path = 'refresher_readings.csv'
        column_name = 'Learning Outcomes'
        title_column_name = 'Title'
        lo_text = read_text_from_csv(
            file_path, title_column_name, column_name, title_value)
        column_name = 'Summary'
        summary_text = read_text_from_csv(
            file_path, title_column_name, column_name, title_value)
        result = [lo_text, summary_text]
    except Exception as e:
        print(f"Error: {str(e)}")
    return result


def get_gpt_response(q_prompt):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "system", "content": "You are a Question Answer generation Bot who generates questions and answers along with brief justifications"},
            {"role": "user", "content": q_prompt},
        ],
        max_tokens=10000,
        stream=True,
    )
    text = ""
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            text = text + chunk.choices[0].delta.content
    return text


def parse_text_to_json(text):
    question_pattern = r'(.+)\nA\)'
    options_pattern = r'[A-D]\)[^\n]+'
    answer_pattern = r'Answer: ([A-D]) with justification - (.+)'

    question_match = re.search(question_pattern, text)
    options_match = re.findall(options_pattern, text)
    answer_match = re.search(answer_pattern, text)

    if question_match and options_match and answer_match:
        question = question_match.group(1).strip()
        options = [option.strip() for option in options_match]
        answer = answer_match.group(1).strip()
        justification = answer_match.group(2).strip()

        return {
            "question": question,
            "options": options,
            "answer": f"Option {answer}",
            "justification": justification
        }
    else:
        return None


def generate_mcq_json(mcqs, topic_name, set='A'):
    question_texts = re.split(r'\d+\.', mcqs)
    json_data = []
    for mcq in question_texts:
        parsed_mcq = parse_text_to_json(mcq)
        if parsed_mcq:
            json_data.append(parsed_mcq)
    filename = generate_filename(topic_name, "json", set)
    save_summary_to_json(json_data, f"json_files/{filename}")
    return json.dumps(json_data, indent=4)


def generate_mcqs(lo_text, summary_text, num_questions=50):
    prompt = f"""
        As a professor tasked with building a quiz question bank from the given summary and learning outcomes, your primary objective is to draft {num_questions} questions adhering to specific guidelines. 
        The summary you have is "{summary_text}" and the learning outcome is "{lo_text}."
        For each question:
        1. Each question must provide four options.
        2. Only one option should be correct, without resorting to "All of the above" or "None of the above."
        3. Structure questions and answers as follows:
        1. Question?
        A) Option 1
        B) Option 2
        C) Option 3
        D) Option 4
        Answer: Option x with justification
        Please ensure that each answer is accompanied by a brief explanation, starting with "Answer:" followed by the correct option and "with justification - " followed by the rationale supporting the answer.
        Example:
        1. What is the capital of France?
        A) London
        B) Berlin
        C) Paris
        D) Madrid
        Answer: C with justification - Paris is the capital of France, known for its iconic landmarks like the Eiffel Tower.
        Now, using the provided summary and learning outcome, generate {num_questions} questions following these guidelines.
    """
    response = get_gpt_response(prompt)

    return response


def formatText(text):
    data_single_line = " ".join(text.strip().splitlines())
    return ' '.join(data_single_line.split())


def get_mcqs(topic_name="", set='A', num_of_question=50):
    mcq_content = ""
    try:
        if len(topic_name):
            result = get_learning_outcome_and_summary_text(topic_name)
            lo_text, summary_text = result
            response = generate_mcqs(formatText(
                lo_text), formatText(summary_text), num_of_question)
            ex_res = generate_mcq_json(response, topic_name, set)
            return ex_res
    except Exception as e:
        print(f"Error: {str(e)}")
    return mcq_content


def save_summary_to_json(json_data, file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(file_path, "w") as json_file:
        json.dump(json_data, json_file, indent=4)
    print("JSON data has been stored to:", file_path)


def generate_filename(topic, filetype, set='A'):
    clean_topic = re.sub(r'[^a-zA-Z0-9\s]', '', topic)
    filename = clean_topic.replace(' ', '_').lower(
    ) + f"_technical_qa_set{set}.{filetype}"
    return filename


def main(set):
    topics = ['Time-Series Analysis', 'Machine Learning',
              'Organizing, Visualizing, and Describing Data']
    for topic in topics:
        mcq_content = get_mcqs(topic, set, 50)
        break
    print("Final", mcq_content)


if __name__ == "__main__":
    set = "A"
    if len(sys.argv) > 1:
        set = sys.argv[1]
    main(set)
