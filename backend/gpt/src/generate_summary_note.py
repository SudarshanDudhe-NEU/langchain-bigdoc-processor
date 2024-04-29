import csv
from openai import OpenAI
from dotenv import load_dotenv
import os

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

def get_gpt_response(q_prompt, max_tokens=500):
    response = client.completions.create(
        model="gpt-4-1106-preview",
        max_tokens=max_tokens,
        prompt=q_prompt
    )
    return response

def generate_technical_notes(learning_outcome, summary):
    query_prompt = """The target user is a financial analyst with an MBA who seeks to enhance their understanding of the LOS.
    Please generate a detailed knowledge summary that covers key insights, concepts, and objectives relevant to the LOS. Ensure the summary incorporates information from the provided LOS sections to offer a holistic understanding. Consider including tables, figures, and equations where necessary to enhance clarity and comprehension."""
    
    text_to_summarize = f"""{query_prompt}\nGive me technical notes for {learning_outcome}\nSummary: {summary}\n"""
    response = get_gpt_response(text_to_summarize)
    return response

def get_learning_outcome_and_summary_text(title_value='Time-Series Analysis'):
    result = []
    try:
        file_path = 'refresher_readings.csv' 
        column_name = 'Learning Outcomes'  
        title_column_name = 'Title'
        lo_text = read_text_from_csv(file_path, title_column_name, column_name, title_value)
        column_name = 'Summary'  
        summary_text = read_text_from_csv(file_path, title_column_name, column_name, title_value)
        result = [lo_text, summary_text]
    except Exception as e:
        print(f"Error: {str(e)}")
    return result

def get_technical_note_summary(title_name=""):
    summary_content = ""
    try:
        if len(title_name):
            result = get_learning_outcome_and_summary_text(title_name)
            lo_text, summary_text = result
            res = generate_technical_notes(lo_text, summary_text)
            summary_content = res.choices[0].text
    except Exception as e:
        print(f"Error: {str(e)}")
    return summary_content

def save_summary_to_md(summary_content, file_path):
    try:
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            print("heheh")
            os.makedirs(directory)
        with open(file_path, "w") as md_file:
            md_file.write(summary_content)
    except Exception as e:
        print(f"Error: {str(e)}")

def main():
    topics=['Time-Series Analysis','Machine Learning','Organizing, Visualizing, and Describing Data']
    for topic in topics:    
        summary_content = get_technical_note_summary(topic)
        save_summary_to_md(summary_content, f"md_files/{topic}_technical_summary.md")
        # break
    # print(summary_content)

if __name__ == "__main__":
    main()
