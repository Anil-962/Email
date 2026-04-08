"""ASGI entrypoint for container runtime."""

from .app import app


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server.main:app", host="0.0.0.0", port=7860)
