import pathlib
import uuid
import re


def generate_filename_by_name(name):
    clean_topic = re.sub(r'[^a-zA-Z0-9\s]', '', name)
    filename = clean_topic.replace(' ', '_').lower()
    return filename


def get_file_location(filename):
    # Generate a random UUID (Universally Unique Identifier)
    unique_string = str(uuid.uuid4())
    path_to_save_file = pathlib.Path.home() / unique_string / "saved_files"
    path_to_save_file.mkdir(parents=True, exist_ok=True)
    file_location = f"{path_to_save_file}/{filename}"
    return file_location
