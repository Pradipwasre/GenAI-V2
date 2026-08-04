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
class Item(BaseModel):
    name : str
    price : float

@app.put("/items/{item_id}")
def update_item(item_id : int , item:Item):
    return {"Item_id" : item_id , "updated_date" : item}

@app.delete("/items/{item_id}")
def delete_item(item_id : int):
    return {"message" : f"Item {item_id} deleted successfully!"}    

@app.get("/student/{student_id}")
def get_student(student_id : int):
    return {"student_id": student_id, "Message" : f"Details for student {student_id}"}


# just try
students_df = {}

class Student(BaseModel):
    name : str
    class_name : str

# Add student
@app.post("students/{student_id}")
def add_student(student_id : int , student:Student):
    students_db[student_id] = student
    return {"Message": f"student {student_id} added" , "student" : student}

# get a student
@app.get("student/{student_id}")
def get_student(student_id : int):
    student = students_df.get(student_id)
    if Student:
        return {"StudentID" : student_id , "Student" : student}
    return {"error" : f"Student {student_id} not found"}
