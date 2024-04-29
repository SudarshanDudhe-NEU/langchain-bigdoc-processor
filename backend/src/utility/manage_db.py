import time
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from dotenv import load_dotenv
import os

load_dotenv()
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
CLUSTER_URL = os.getenv("CLUSTER_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME")


def connect_to_mongodb():
    connection_string = f"mongodb+srv://{USERNAME}:{PASSWORD}@{CLUSTER_URL}/{DATABASE_NAME}?retryWrites=true&w=majority&appName=clusterSD"
    try:
        client = MongoClient(connection_string)
        # client.admin.command('ping')
        print("Connection established to MongoDB")
        db = client[DATABASE_NAME]
        return db
    except ServerSelectionTimeoutError:
        print("Server selection timeout. Could not connect to MongoDB.")
        return None
    except ConnectionFailure:
        print("Failed to connect to MongoDB. Check your connection settings.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def connect_to_mongodb_collection(collection_name):
    db = connect_to_mongodb()
    if db:
        collection = db[collection_name]
        return collection
    else:
        return None


def saveUserToDb(email, username, name):
    try:
        user = {
            "name": name,
            "username": username,
            "email": email
        }
        result = saveDocumentToDb('User', user)
        print("user inserted to db")
        return result
    except Exception as e:
        print("Error in Storing user to DB", e)


def saveDocumentToDb(collection_name, doc):
    try:
        collection = connect_to_mongodb_collection(collection_name)
        collection.insert_one(doc)
    except Exception as e:
        print("Error in Storing user to DB", e)
        return None


def saveUserFileDetailsToDb(user_id, data):
    try:
        doc = {"user_id": user_id, 'file_name': data["file_name"],
               'summary': data["summary"]}
        file_name = doc["file_name"]

        collection = connect_to_mongodb_collection("UserFileDetails")
        result = collection.find({"file_name": file_name})
        count = result.count()
        if count:
            _file_name = f'{file_name}-{count}'
            doc['file_name'] = _file_name
        saveDocumentToDb("UserFileDetails", doc)
    except Exception as e:
        print("Error in Storing user to DB", e)
        return None


def get_user_file_details(user_id):
    try:
        collection = connect_to_mongodb_collection("UserFileDetails")
        result = collection.find({"user_id": user_id})
        return result
    except Exception as e:
        print("Error in Storing user to DB", e)
        return None


def get_user_file_summary(user_id, file_name):
    try:
        collection = connect_to_mongodb_collection("UserFileDetails")
        result = collection.find_one(
            {"user_id": user_id, "file_name": file_name})
        return result
    except Exception as e:
        print("Error in Storing user to DB", e)
        return None
