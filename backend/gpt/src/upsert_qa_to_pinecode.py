import sys
import json
import os
import re
import string
import random
from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec
from langchain.text_splitter import RecursiveCharacterTextSplitter

load_dotenv()

# Initialize Pinecone and OpenAI clients
pinecone_client = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# Function to chunk and embed text data
def chunk_and_embed(data):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=20,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = splitter.split_text(data)
    embeddings = openai_client.embeddings.create(
        input=chunks,
        model="text-embedding-3-small"
    )
    return chunks, embeddings


# Function to create Pinecone index if not already existing
def create_index(index_name):
    print("Creating Pinecone index...")
    if index_name not in pinecone_client.list_indexes().names():
        # Create the index with specified configuration
        pinecone_client.create_index(
            name=index_name,
            dimension=1536,
            metric='cosine',
            spec=ServerlessSpec(
                cloud='aws',
                region='us-east-1'
            )
        )
        print("Pinecone index created successfully.")


# Function to upsert data into Pinecone
def upsert_into_pinecone(index_name, namespace_name, data_chunks, embeddings):
    embedding_to_upsert = []
    # Iterate over chunks and their embeddings
    for i, chunk in enumerate(data_chunks):
        # Generate a unique ID for each chunk
        rand_chunk_code = ''.join(random.choices(
            string.ascii_letters + string.digits, k=3))
        # Append the chunk embedding and metadata to upsert list
        embedding_to_upsert.append({'id': f'doc-summ-{rand_chunk_code}',
                                    'values': embeddings.data[i].embedding, 'metadata': {'text': chunk}})
    try:
        # Get the index object
        index = pinecone_client.Index(index_name)
        # Upsert embeddings into the index
        index.upsert(vectors=list(embedding_to_upsert),
                     namespace=namespace_name)
        print("Data upserted into Pinecone successfully.")
    except Exception as e:
        print(f"Error occurred while upserting into Pinecone: {e}")


# Function to generate a filename for JSON data
def generate_filename(topic, filetype, separator='_', set='A'):
    clean_topic = re.sub(r'[^a-zA-Z0-9\s]', '', topic)
    filename = clean_topic.replace(
        ' ', separator).lower() + f"_technical_qa_set{set}.{filetype}"
    return filename


# Function to read QA data from a JSON file
def get_qa_from_file(file_path):
    try:
        print(f"Reading QA data from file...{file_path}")
        with open(file_path, "r") as json_file:
            json_data = json.load(json_file)
        print("QA data read successfully.")
        return json_data
    except Exception as e:
        print(f"Error occurred while reading MD file: {e}")
        return None


# Function to generate markdown from JSON QA data
def generate_markdown_from_json(data):
    markdown_text = ""
    markdown_text += f"### {data['question']}\n\n"
    for option in data['options']:
        markdown_text += f"{option}\n"
    markdown_text += f"\nAnswer: {data['answer']} with justification - {data['justification']}\n\n"
    return markdown_text


def split_and_upsert(index_name, raw_text, namespace):
    try:
        # Chunk and embed the markdown text
        qa_chunks, embeddings = chunk_and_embed(raw_text)
        # Upsert embeddings into Pinecone
        upsert_into_pinecone(index_name, namespace, qa_chunks, embeddings)
    except Exception as e:
        print(f"Error processing QA data: {str(e)}")


# Function to get questions from JSON files and upsert into Pinecone
def get_question_and_upsert(topic, set='A'):
    try:
        # Generate the filename for the JSON data
        filename = generate_filename(topic, 'json', '_', set)
        file_path = f"json_files/{filename}"
        if os.path.exists(file_path):
            print(file_path)
            print("Processing QA data...")
            json_data = get_qa_from_file(file_path)
            if len(json_data):
                # Create Pinecone index if not already existing
                create_index('study-bot')
                for qa_data in json_data:
                    try:
                        markdown_text = generate_markdown_from_json(qa_data)
                        # Chunk and embed the markdown text
                        qa_chunks, embeddings = chunk_and_embed(markdown_text)
                        # Get the filename without extension
                        filename = filename.split(".")[0]
                        # Upsert embeddings into Pinecone
                        upsert_into_pinecone('study-bot',
                                             f'{filename}', qa_chunks, embeddings)
                    except Exception as e:
                        print(f"Error processing QA data: {str(e)}")
        else:
            print(f"File '{file_path}' does not exist.")
    except Exception as e:
        print(f"Error: {str(e)}")


# # Main function to iterate over topics and process QA data
# def main(set):
#     topics = ['Machine Learning',
#               'Organizing, Visualizing, and Describing Data']
#     for topic in topics:
#         get_question_and_upsert(topic, set)
#         break


# # Entry point of the script
# if __name__ == "__main__":
#     set = "A"
#     if len(sys.argv) > 1:
#         set = sys.argv[1]
#     main(set)
