
# Langchain Big Document Processor

## Overview
The **Langchain Big Document Processor** is a powerful tool designed to streamline the process of document analysis and summary generation. It leverages GPT-4, an advanced language model, to generate concise summaries from text documents (PDF or TXT) or YouTube transcripts. This tool is capable of accurately summarizing hundreds of pages of text by utilizing cutting-edge natural language processing techniques. Built with Python and Streamlit, the **Langchain Big Document Processor** provides an intuitive and user-friendly interface for document summarization. It leverages the langchain library for text processing, ensuring high-quality summaries that capture the essence of the input document.

### Demo
Try out the **langchain-bigdoc-processor** tool [here](http://64.23.141.212:8501/).


## Features
- Supports PDF and TXT file formats
- Utilizes GPT-4 for generating summaries
- Automatic clustering of the input document to identify key sections
- Customizable number of clusters for the summarization process

## Project Structure

```
.
├── Dockerfile
├── README.md
├── backend
│   ├── Dockerfile
│   ├── __init__.py
│   ├── gpt
│   │   ├── Dockerfile
│   │   ├── __init__.py
│   │   ├── refresher_readings.csv
│   │   ├── requirements.txt
│   │   └── src
│   │       ├── generate_mcqs.py
│   │       ├── generate_summary_note.py
│   │       ├── upsert_qa_to_pinecode.py
│   │       └── upsert_summary_to_pinecode.py
│   ├── logging.conf
│   ├── process_questions_from_setA.py
│   ├── requirement.txt
│   ├── requirements.txt
│   └── src
│       ├── main.py
│       ├── requirements.txt
│       └── utility
│           ├── backend.py
│           ├── elbow.py
│           ├── file_utils.py
│           ├── gpt_utilis.py
│           ├── instructorembeddings.py
│           ├── manage_db.py
│           ├── my_prompts.py
│           ├── pydantic_models.py
│           ├── summariztion_utils.py
│           ├── summazire.py
│           └── text_utils.py
├── docker-compose.yaml
├── frontend
│   ├── Dockerfile
│   ├── __init__.py
│   ├── requirement.txt
│   ├── requirements.txt
│   └── src
│       ├── ask_question.py
│       ├── main.py
│       ├── summarization.py
│       └── utility.py
└── requirements_back.txt

```


## How to Run the Application Locally

1. Clone the repository:
    ```bash
    git clone https://github.com/SudarshanDudhe-NEU/langchain-bigdoc-processor.git
    ```

2. Navigate to the project directory:
    ```bash
    cd langchain-bigdoc-processor
    ```

3. Build and start the application using Docker Compose:
    ```bash
    docker-compose up --build
    ```

4. Once the containers are up and running, access the application by navigating to `http://localhost:8501` in your web browser.

5. Select a file and ask a question to trigger the summarization process and get answers based on your document.

6. View the result in the application.


## References

•	https://python.langchain.com/docs/get_started/introduction/
•	https://platform.openai.com/docs/introduction
•	https://docs.pinecone.io/guides/getting-started/quickstart/Using_Pinecone_for_embeddings_search.ipynb
•	https://github.com/openai/openai-cookbook/blob/main/examples/vector_databases/pinecone/
•	https://github.com/openai/openai-cookbook/blob/main/examples/vector_databases/pinecone/GPT4_Retrieval_Augmentation.ipynb
•	https://github.com/pinecone-io/examples/tree/master/learn/search/question-answering
     

