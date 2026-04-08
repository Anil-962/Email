# Use the official Python 3.11 slim image for a smaller footprint
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Environment variables to optimize Python execution in containers
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy the requirements file first to leverage caching for dependencies
COPY requirements.txt .

# Install Python dependencies without caching them to keep the image small
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the Hugging Face NLP model so the container boots quickly
RUN python -c "from transformers import pipeline; pipeline('zero-shot-classification', model='typeform/distilbert-base-uncased-mnli')"

# Copy the rest of the source code into the container
COPY . .

# Expose the port that the application runs on
EXPOSE 8000

# Start the application using uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
