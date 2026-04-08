FROM python:3.10-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PORT=7860

COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip \
    && pip install -r /app/requirements.txt

# Copy only required runtime files.
COPY server /app/server
COPY my_env /app/my_env
COPY models.py /app/models.py
COPY client.py /app/client.py
COPY __init__.py /app/__init__.py
COPY openenv.yaml /app/openenv.yaml
COPY inference.py /app/inference.py

# Hugging Face Spaces requirement.
EXPOSE 7860

CMD ["sh", "-c", "uvicorn server.main:app --host 0.0.0.0 --port ${PORT:-7860}"]
