# File: /Users/pradipwasre/Desktop/GenAI-V2/FastAPI/01_hello_server.py

from fastapi import FastAPI

# Create FastAPI app instance
app = FastAPI()

# Define a simple GET endpoint
@app.get("/")
def read_root():
    return {"Todays update": "Weather in Pune is 24°!"}

@app.get("/address")
def get_address():
    return {"address" : "Maharashtra  Pune - 24 Degrees with rain"}


@app.get("/rain")
def get_rain():
    return {"Rain News" : "Current Seasonal Total: 880.5 mm (recorded by August 2, 2026)."}

@app.get("/demographic")
def demographics():
    return {"Total Population:" :{"Estimated at 1,476,625,576 at mid-year 2026."}}