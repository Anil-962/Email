# Use the official Python 3.11 slim image
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# First, install the bare minimum root requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Then, copy the openenv environment setup and install it 
# (This installs all the local environment tools like fastmcp, openenv-core etc)
COPY my_env/pyproject.toml ./my_env/
COPY my_env/server/requirements.txt ./my_env/server/
RUN pip install --no-cache-dir -r ./my_env/server/requirements.txt
COPY my_env ./my_env
RUN pip install --no-cache-dir -e ./my_env

# Copy the lightweight placeholder app
COPY main.py .

EXPOSE 8000
EXPOSE 8001
EXPOSE 8002

# Default entrypoint for the container (overridden in docker-compose.yml per service)
CMD ["python", "main.py"]
