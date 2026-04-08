FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install only runtime deps required by the FastAPI backend used in Space.
COPY my_env/server/requirements.space.txt /app/requirements.space.txt
RUN pip install --no-cache-dir -r /app/requirements.space.txt

# Copy backend package source.
COPY my_env /app/my_env

# Hugging Face Spaces expects the app on port 7860 (or PORT env var).
EXPOSE 7860

CMD ["sh", "-c", "uvicorn my_env.server.main:app --host 0.0.0.0 --port ${PORT:-7860}"]
