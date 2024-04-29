FROM python:3.9-slim

WORKDIR /app

RUN pip install streamlit

COPY ./ /app/frontend/

RUN pip install --no-cache-dir --use-deprecated=legacy-resolver -r /app/frontend/requirements.txt

EXPOSE 8501

# CMD ["bash", "-c", "python frontend/logger.py && streamlit run /app/frontend/main.py --server.port=8501 --server.address=0.0.0.0"]
CMD ["streamlit", "run", "/app/frontend/src/main.py", "--logger.level=warning", "2>'/app/frontend/app_log.log'", "--server.port=8501", "--server.address=0.0.0.0"]