from fastapi import FastAPI
from pydantic import BaseModel

# Create FastAPI app instance
app = FastAPI()

# ---------------- GET Endpoints ----------------
@app.get("/")
def read_root():
    return {"Todays update": "Weather in Pune is 24°!"}

@app.get("/address")
def get_address():
    return {"address": "Maharashtra  Pune - 24 Degrees with rain"}

@app.get("/rain")
def get_rain():
    return {"Rain News": "Current Seasonal Total: 880.5 mm (recorded by August 2, 2026)."}

@app.get("/demographic")
def demographics():
    return {"Total Population:": {"Estimated at 1,476,625,576 at mid-year 2026."}}

# ---------------- POST Endpoints ----------------

class Item(BaseModel):
    name : str 
    price: float

@app.post("/items/")
def create_item(item : Item):
    return {"message" : f"Iteam : '{item.name}' with price {item.price}"}

@app.post("/item/")
def create(item : dict):
    return {"received_data" : item}





# ---------------- PUT Endpoint ----------------
# Example: Update existing profile
class UpdateProfile(BaseModel):
    username: str
    email: str
    age: int

@app.put("/profile")
def update_profile(profile: UpdateProfile):
    return {
        "status": "updated",
        "updated_profile": {
            "username": profile.username,
            "email": profile.email,
            "age": profile.age
        }
    }
