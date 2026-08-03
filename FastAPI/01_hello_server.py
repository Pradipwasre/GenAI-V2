# File: /Users/pradipwasre/Desktop/GenAI-V2/FastAPI/01_hello_server.py

from fastapi import FastAPI

# Create FastAPI app instance
app = FastAPI()

# Define a simple GET endpoint
@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI is working!"}
