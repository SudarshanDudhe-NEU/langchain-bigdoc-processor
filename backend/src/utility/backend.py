from pathlib import Path
from fastapi import FastAPI, UploadFile, File
import uvicorn
from backend.src.utility.summazire import process_summarize_button

app = FastAPI()


@app.get("/test")
def test():
    print(Path.home())
    return {"message": "Running"}


@app.post("/file/upload")
async def upload_file(username: str, uploaded_file: UploadFile = File(...)):
    path_to_save_file = Path.home() / username / "saved_files"
    path_to_save_file.mkdir(parents=True, exist_ok=True)
    file_location = f"{path_to_save_file}/{uploaded_file.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(uploaded_file.file.read())
    file_location
    use_gpt_4 = True
    find_clusters = False
    summary = process_summarize_button(file_location, api_key,
                                       use_gpt_4, find_clusters, file=True)
    print(summary)
    return {"INFO": f"File '{uploaded_file.filename}' saved to your profile.", "summary": summary}


@app.post("/summarize/")
async def summarize(uploaded_file: UploadFile = File(...), youtube_url: str = "", api_key: str = "", use_gpt_4: bool = True, find_clusters: bool = False):
    # doc = transcript_loader(youtube_url)
    print(youtube_url)

    summary = process_summarize_button(uploaded_file, api_key,
                                       use_gpt_4, find_clusters, file=True)
    print(summary)
    return ({"summary": summary})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
