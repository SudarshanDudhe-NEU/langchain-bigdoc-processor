FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --use-deprecated=legacy-resolver -r /app/requirements.txt
RUN python -m pip install "pymongo[srv]"

COPY ./ /app/backend/

EXPOSE 8000

CMD ["uvicorn", "backend.src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
 