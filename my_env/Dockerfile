FROM python:3.11-slim

WORKDIR /workspace

# Copy project files
COPY . .

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies from pyproject.toml
RUN pip install --no-cache-dir -e .

# Expose port 7860
EXPOSE 7860

# Run FastAPI app with uvicorn
CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "7860"]
