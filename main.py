import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "FastAPI is running!"}

if __name__ == "__main__":
    # Use PORT environment variable provided by Render, default to 8000
    port = int(os.environ.get("PORT", 8000))
    # Run uvicorn server
    uvicorn.run("main:app", host="0.0.0.0", port=port)
