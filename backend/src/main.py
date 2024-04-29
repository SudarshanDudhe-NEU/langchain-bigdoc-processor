import json
import os
import logging
import pathlib

from fastapi import FastAPI, Path, HTTPException, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

import openai
from pinecone import Pinecone

from backend.src.utility.gpt_utilis import *
from backend.src.utility.manage_db import saveUserToDb, saveUserFileDetailsToDb, get_user_file_details, get_user_file_summary
from backend.src.utility.summazire import process_summarize_button
from backend.gpt.src.upsert_qa_to_pinecode import split_and_upsert
from backend.src.utility.file_utils import get_file_location, generate_filename_by_name
# Load environment variables
load_dotenv()

# get root logger
# the __name__ resolve to "main" since we are at the root of the project.
logger = logging.getLogger(__name__)
# This will get the root logger since no logger in the configuration has this name.

# Initialize FastAPI app
app = FastAPI()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
# Initialize OpenAI and Pinecone clients
client = openai.OpenAI(api_key=OPENAI_API_KEY)
MODEL = "text-embedding-3-small"
pinecone_client = Pinecone(api_key=PINECONE_API_KEY)
print(pinecone_client)
index_name = 'study-bot'

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://frontend:8501"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


@app.get("/")
def hello():
    """
    Returns a simple message to indicate the backend is running.
    """
    logger.info(f"Backend is running.")
    return {"message": "Backend is running"}


@app.get("/get_data")
def get_sf_data():
    """
    Fetches data. Placeholder function, currently returning an empty list.
    """
    try:
        data = []
        logger.info(f"Success fetching data.")
        return {"data": data}
    except Exception as e:
        logger.error(f"Error fetching data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/get_file_names_data/{user_id}")
def get_file_names_data(user_id: str):
    """
    Retrieves file names data for a specific user ID.
    """
    try:
        result = get_user_file_details(user_id)
        data = []
        if result:
            data = [doc["file_name"] for doc in result]
            print(data)
            return JSONResponse(content={"data": data})
        else:
            raise HTTPException(
                status_code=404, detail=f"File names data not found.")
    except Exception as e:
        logger.error(f"Error fetching summary data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/get_file_summary_data/{user_id}/{selected_file}")
def get_file_summary_data(user_id: str = Path(...), selected_file: str = Path(...)):
    """
    Retrieves summary data for a specific user ID and selected file.
    """
    try:
        result = get_user_file_summary(user_id, selected_file)
        if result:
            data = result["summary"]
            return JSONResponse(content={"data": data})
        else:
            raise HTTPException(
                status_code=404, detail=f"File names data not found.")
    except Exception as e:
        logger.error(f"Error fetching summary data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/get_summary_data/{topic_name}")
def get_summary_data(topic_name: str = Path(...)):
    """
    Retrieves summary data for a specific topic name.
    """
    try:
        local_folder_path = f"/app/backend/src/md_files/"
        file_name = f"{topic_name}_technical_summary.md"
        local_file_path = os.path.join(
            local_folder_path, os.path.basename(file_name))
        if os.path.exists(local_file_path):
            with open(local_file_path, "r") as md_file:
                summary_content = md_file.read()
            return {"data": summary_content}
        else:
            raise HTTPException(
                status_code=404, detail=f"Summary data for topic '{topic_name}' not found.")
    except Exception as e:
        logger.error(f"Error fetching summary data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/get_qa_data/{topic_name}/{set_name}")
def get_qa_data(topic_name: str = Path(...), set_name: str = Path(...)):
    """
    Retrieves QA data for a specific topic name and set name.
    """
    try:
        qa_data = []
        file_name = generate_qa_filename(topic_name, "json", set_name)
        local_folder_path = f"/app/backend/src/json_files/"
        local_file_path = os.path.join(
            local_folder_path, os.path.basename(file_name))
        if os.path.exists(local_file_path):
            with open(local_file_path, "r") as file:
                qa_data = file.read()
            return {"data": qa_data}
        else:
            raise HTTPException(
                status_code=404, detail=f"QA data for topic '{topic_name}' not found.")
    except Exception as e:
        logger.error(f"Error fetching QA data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/get_answer_by_gpt_with_pc_summary_context")
def get_answer_by_gpt_with_pc_summary_context(req_data: ReqData, answer_in_markdown_text=True):
    """
    Retrieves an answer using GPT with PC summary context.
    """
    result = {"markdown_text": "", "answer": None}
    try:
        question_dict = req_data.question
        topic = req_data.topic
        question_markdown_text = gen_markdown_from_question(question_dict)
        answer_instance = get_answer_by_summary_from_gpt(
            question_markdown_text, topic)
        logger.info(
            f"Answer by GPT with PC summary context: {answer_instance}")
        if answer_in_markdown_text:
            answer_markdown_text = gen_markdown_from_Answer(
                answer_instance)
            result["markdown_text"] = answer_markdown_text
        else:
            result['answer'] = answer_instance
    except Exception as e:
        logger.error(
            f"Error fetching answer by GPT with PC summary context: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    return result


@app.post("/get_answer_by_gpt_with_pc_qa_context")
def get_answer_by_gpt_with_pc_qa_context(req_data: ReqData, answer_in_markdown_text=True):
    """
    Retrieves an answer using GPT with PC QA context.
    """
    result = {"markdown_text": "", "answer": None}
    try:
        req_data = ReqData(**req_data)
        question_dict = req_data.question
        topic = req_data.topic
        question_markdown_text = gen_markdown_from_question(question_dict)
        answer_instance = get_answer_by_gpt_vector_from_pc(
            question_markdown_text, topic)
        logger.info(f"Answer by GPT with PC QA context: {answer_instance}")
        if answer_in_markdown_text:
            answer_markdown_text = gen_markdown_from_Answer(answer_instance)
            result["markdown_text"] = answer_markdown_text
        else:
            result['answer'] = answer_instance
    except Exception as e:
        print(str(e))
        logger.error(
            f"Error fetching answer by GPT with PC QA context: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    return result


@app.get("/answer_stats/{based}")
def get_answer_stats(based: str):
    """
    Retrieves answer statistics based on the provided parameter.
    """
    try:
        folder_path = "backend/results/"
        if based == "qa_based":
            file_path = os.path.join(folder_path, 'results.json')
        elif based == "summary_based":
            file_path = os.path.join(folder_path, 'sum_results.json')
        with open(file_path, "r") as f:
            data = json.load(f)
        total_answers = len(data)
        correct_answers = sum(question["is_correct"] for question in data)
        wrong_answers = total_answers - correct_answers
        return {
            "total_answers": total_answers,
            "correct_answers": correct_answers,
            "wrong_answers": wrong_answers,
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="results.json not found")
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500, detail="Error parsing results.json")
    except KeyError as e:
        raise HTTPException(
            status_code=500, detail=f"Missing key in results.json: {e}")
    except TypeError as e:
        raise HTTPException(status_code=500, detail=f"Type error: {e}")


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Uploads a file and retrieves its summary.
    """
    try:
        response = {'file_name': "", 'summary': ""}
        if file:
            response['file_name'] = file.filename
            file_location = get_file_location(file.filename)
            with open(file_location, "wb+") as file_object:
                file_object.write(file.file.read())
            print(file_location)
            use_gpt_4 = True
            find_clusters = False
            summary = process_summarize_button(file_location, OPENAI_API_KEY,
                                               use_gpt_4, find_clusters, file=True)
            if summary:
                response['summary'] = summary
                try:
                    saveUserFileDetailsToDb(
                        "662c7428fb45c882e17567b8", response)
                    print("saved to db")
                    upsert(file_location, file.filename)
                except Exception as e:
                    print(str(e))

        return JSONResponse(status_code=200, content=response)
    except HTTPException as http_exc:
        return JSONResponse(status_code=http_exc.status_code, content={"detail": http_exc.detail})
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"An unexpected error occurred: {str(e)}"})


# @app.post("/file/upload")
# async def upload_file_and_get_summary(username: str, uploaded_file: UploadFile = File(...), use_gpt_4=True, find_clusters=False):
#     """
#     Uploads a file and retrieves its summary.
#     """
#     try:
#         print(username)
#         print(uploaded_file.filename)
#         response = {'file_name': "", 'summary': ""}
#         if uploaded_file:
#             response['file_name'] = uploaded_file.filename
#             file_location = get_file_location(username, uploaded_file.filename)
#             with open(file_location, "wb+") as file_object:
#                 file_object.write(uploaded_file.file.read())
#             print(file_location)
#             summary = process_summarize_button(file_location, OPENAI_API_KEY,
#                                                use_gpt_4, find_clusters, file=True)
#             if summary:
#                 response['summary'] = summary
#                 try:
#                     saveUserFileDetailsToDb(
#                         "662c7428fb45c882e17567b8", response)
#                     print("saved to db")
#                     upsert(file_location, uploaded_file.filename)
#                 except Exception as e:
#                     print(str(e))
#         return response
#     except Exception as e:
#         print(str(e))


def upsert(file_location, filename):
    index = pinecone_client.Index(index_name)
    namespace_list = index.describe_index_stats()["namespaces"].keys()
    if len(namespace_list):
        namespace = generate_filename_by_name(filename)
        print("namespace in namespace_list")
        print(namespace in namespace_list)
        if namespace not in namespace_list:
            upsert_file_content(index_name, file_location, namespace)


@app.post("/get_answer_by_chain")
def get_answer_by_chain(query: QueryData):
    """
    Placeholder function. It seems incomplete and lacking proper context.
    """
    # query = "How much the agriculture target will be increased to and what the focus will be"
    answer_response = get_chain_run_result(
        query.question, index_name, query.filename)
    if answer_response["code"] == 200:
        answer = answer_response["answer"]
        answer_obj = QueryAnswer(answer=answer)
        return {"message": "Success", "data": answer_obj.model_dump_json()}
    elif answer_response["code"] == 404:
        raise HTTPException(status_code=404, detail=answer_response["answer"])
    elif answer_response["code"] == 500:
        raise HTTPException(status_code=500, detail=answer_response["answer"])


# class UserName(BaseModel):
#     username: str


# # @app.post("/getJobSuggesions")
# # def getSuggesions(request: Request, file: UploadFile = File(...)):
# #     try:
# #         jjj = request.json()
# #         print(request.body())
# #         print(dir(request))
# #         print(file)
# #         # username = request.username
# #     except Exception as e:
# #         print(str(e))


# # class FileParams(BaseModel):
# #     name: str
# #     description: str


# # @app.post("/upload/")
# # async def upload_file(params: FileParams, file: UploadFile = File(...)):
# #     return {"file_name": file.filename, "name": params.name, "description": params.description}
