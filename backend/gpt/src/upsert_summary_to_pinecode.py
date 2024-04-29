import os
from openai import OpenAI
from dotenv import load_dotenv

from pinecone import Pinecone, ServerlessSpec
from langchain.text_splitter import RecursiveCharacterTextSplitter
import string
import random
from dotenv import load_dotenv

load_dotenv()

pinecone_client = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# Function to chunk and embed data
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


def create_index(index_name='cfa-articles-summary'):

    # # Check whether the index with the same name already exists - if so, delete it
    # if index_name in pinecone_client.list_indexes():
    #     pinecone_client.delete_index(index_name)

    # Now do stuff
    print(pinecone_client.list_indexes().names())
    if index_name not in pinecone_client.list_indexes().names():
        pinecone_client.create_index(
            name=index_name,
            dimension=1536,
            metric='dotproduct',
            spec=ServerlessSpec(
                cloud='aws',
                region='us-west-2'
            )
        )

# Function to upsert data into Pinecone


def upsert_into_pinecone(namespace, data_chunks, embeddings):
    embedding_to_upsert = []
    for i, chunk in enumerate(data_chunks):
        rand_chunk_code = ''.join(random.choices(
            string.ascii_letters + string.digits, k=3))
        embedding_to_upsert.append({'id': f'doc-summ-{rand_chunk_code}',
                                   'values': embeddings.data[i].embedding, 'metadata': {'text': chunk}})
    try:
        create_index()
        index = pinecone_client.Index('cfa-articles-summary')
        index.upsert(vectors=list(embedding_to_upsert),
                     namespace=namespace)
    except Exception as e:
        print(f"Error occurred while upserting into Pinecone: {e}")


def get_summary_from_md(file_path):
    try:
        with open(file_path, "r") as md_file:
            summary_content = md_file.read()
        return summary_content
    except Exception as e:
        print(f"Error occurred while reading MD file: {e}")
        return None


# Function to generate GPT summary and upsert into Pinecone
def get_summary_and_upsert(topic):
    # Get GPT summary
    file_path = f"md_files/{topic}_technical_summary.md"
    if os.path.exists(file_path):
        summary_content = get_summary_from_md(file_path)

        # Chunk and embed GPT summary
        summary_chunks, embeddings = chunk_and_embed(summary_content)

        # Upsert embeddings into Pinecone
        upsert_into_pinecone(
            f'doc-summary-{topic.replace(" ", "-")}', summary_chunks, embeddings)
    else:
        print(f"File '{file_path}' does not exist.")


def main():
    try:
        topics = ['Time-Series Analysis', 'Machine Learning',
                  'Organizing, Visualizing, and Describing Data']
        for topic in topics:
            get_summary_and_upsert(topic)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
