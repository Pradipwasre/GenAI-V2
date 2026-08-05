"""
============================================================
HOW TO RUN:
1. Install dependencies:
   pip install fastapi uvicorn

2. Run the server:
   uvicorn main:app --reload
   (Replace 'main' with your filename without .py)

3. Open your browser and visit:
   http://127.0.0.1:8000/docs
   This shows auto-generated interactive documentation!

============================================================
"""

from fastapi import FastAPI, Query, Path
from pydantic import BaseModel
from typing import Optional, List

# ============================================================
# STEP 1: CREATE THE APP (The Server)
# ============================================================
# FastAPI is a modern Python web framework used to build APIs.
# It automatically handles:
#   - Data validation
#   - Documentation generation (Swagger UI at /docs)
#   - Error handling
# ============================================================

app = FastAPI(
    title="The Quick FastAPI",
    description="Fasted way to connected APIs",
    version="1.0.0"
)

# In-memory "database" for demonstration
# In real projects, use a proper database like PostgreSQL or MongoDB
customers_db = [
    {"id": 1, "name": "Rahul", "city": "Bangalore", "risk": "low"},
    {"id": 2, "name": "Priya", "city": "Bangalore", "risk": "high"},
    {"id": 3, "name": "Amit", "city": "Mumbai", "risk": "high"},
    {"id": 4, "name": "Sneha", "city": "Delhi", "risk": "low"},
]

predictions_db = []


# ============================================================
# STEP 2: BASIC ENDPOINT - GET METHOD
# ============================================================
# GET is used to RETRIEVE data.
# Example: Viewing a web page, fetching weather data.
# 
# Endpoint: /
# Purpose: Welcome message (like a homepage)
# ============================================================

@app.get("/")
def home():
    """
    This is the root endpoint.
    When you visit http://127.0.0.1:8000/, you see this message.

    Think of it like the homepage of a website.
    """
    return {
        "message": "Welcome to FastAPI Tutorial!",
        "note": "Visit /docs to see interactive API documentation"
    }


# ============================================================
# STEP 3: GET ALL CUSTOMERS (Retrieve data)
# ============================================================
# URL: http://127.0.0.1:8000/customers
# Method: GET
# Returns: List of all customers in JSON format
# ============================================================

@app.get("/customers")
def get_all_customers():
    """
    GET /customers

    Returns all customers from our database.
    JSON looks like a Python dictionary and is used to 
    exchange data between client and server.
    """
    return {
        "status": "success",
        "count": len(customers_db),
        "data": customers_db
    }


# ============================================================
# STEP 4: PATH PARAMETERS - Identify a specific resource
# ============================================================
# Path parameters are EMBEDDED directly inside the URL.
# They are used to identify ONE specific item.
# 
# Example: /customer/{customer_id}
# customer_id is a dynamic value that changes with each request.
# 
# Try: http://127.0.0.1:8000/customer/1
# Try: http://127.0.0.1:8000/customer/2
# ============================================================

@app.get("/customer/{customer_id}")
def get_customer_by_id(
    customer_id: int = Path(..., description="The ID of the customer to retrieve", ge=1)
):
    """
    GET /customer/{customer_id}

    Path Parameter: customer_id (embedded in the URL)

    This finds ONE specific customer by their ID.
    Path parameters are best for identifying a specific item.

    Example URLs:
      /customer/1  -> Returns Rahul
      /customer/2  -> Returns Priya
    """
    # Search for the customer in our database
    customer = None
    for c in customers_db:
        if c["id"] == customer_id:
            customer = c
            break

    if customer:
        return {
            "status": "success",
            "data": customer
        }
    else:
        return {
            "status": "error",
            "message": f"Customer with ID {customer_id} not found"
        }


# ============================================================
# STEP 5: QUERY PARAMETERS - Filter or customize response
# ============================================================
# Query parameters are added AFTER a ? at the end of the URL.
# They are used to FILTER or CUSTOMIZE the response.
# 
# Example: /customers?city=Bangalore&risk=high
# This filters only high-risk customers from Bangalore.
# 
# Try: http://127.0.0.1:8000/customers/filter?city=Bangalore
# Try: http://127.0.0.1:8000/customers/filter?risk=high
# Try: http://127.0.0.1:8000/customers/filter?city=Bangalore&risk=high
# ============================================================

@app.get("/customers/filter")
def filter_customers(
    city: Optional[str] = Query(None, description="Filter by city name"),
    risk: Optional[str] = Query(None, description="Filter by risk level (low/high)")
):
    """
    GET /customers/filter?city=...&risk=...

    Query Parameters: city, risk (added after ? in the URL)

    This filters the customer list based on query parameters.
    Query parameters are best for filtering or customizing results.

    Example URLs:
      /customers/filter?city=Bangalore
      /customers/filter?risk=high
      /customers/filter?city=Bangalore&risk=high
    """
    result = customers_db.copy()

    # Apply city filter if provided
    if city:
        result = [c for c in result if c["city"].lower() == city.lower()]

    # Apply risk filter if provided
    if risk:
        result = [c for c in result if c["risk"].lower() == risk.lower()]

    return {
        "status": "success",
        "filters_applied": {
            "city": city,
            "risk": risk
        },
        "count": len(result),
        "data": result
    }


# ============================================================
# STEP 6: POST METHOD - Submit new data
# ============================================================
# POST is used to CREATE / SUBMIT new data.
# Example: Filling a form, creating a new account.
# 
# We use Pydantic models to define the expected data format.
# FastAPI automatically validates the data for us!
# ============================================================

class CustomerCreate(BaseModel):
    """
    This Pydantic model defines what data we expect
    when creating a new customer.

    FastAPI uses this to:
      - Validate the incoming JSON
      - Show the expected format in /docs
      - Convert data automatically
    """
    name: str
    city: str
    risk: str  # "low" or "high"


@app.post("/customers")
def create_customer(customer: CustomerCreate):
    """
    POST /customers

    Creates a new customer.
    The client sends JSON data in the request body.

    Example request body (JSON):
    {
        "name": "Vikram",
        "city": "Chennai",
        "risk": "low"
    }

    FastAPI automatically:
      - Reads the JSON
      - Validates it matches CustomerCreate model
      - Returns helpful errors if data is wrong
    """
    # Generate a new ID
    new_id = max([c["id"] for c in customers_db], default=0) + 1

    # Create the new customer
    new_customer = {
        "id": new_id,
        "name": customer.name,
        "city": customer.city,
        "risk": customer.risk
    }

    # Save to our "database"
    customers_db.append(new_customer)

    return {
        "status": "success",
        "message": "Customer created successfully",
        "data": new_customer
    }


# ============================================================
# STEP 7: PUT METHOD - Update existing data
# ============================================================
# PUT is used to UPDATE existing data.
# Example: Editing a profile, changing account details.
# ============================================================

class CustomerUpdate(BaseModel):
    """
    Model for updating a customer.
    All fields are optional because you might update
    only one field at a time.
    """
    name: Optional[str] = None
    city: Optional[str] = None
    risk: Optional[str] = None


@app.put("/customer/{customer_id}")
def update_customer(
    customer_id: int = Path(..., description="ID of customer to update"),
    update_data: CustomerUpdate = ...
):
    """
    PUT /customer/{customer_id}

    Updates an existing customer.
    Uses both:
      - Path Parameter: customer_id (which customer to update)
      - Request Body: update_data (what to change)

    Example: PUT /customer/1
    Request body:
    {
        "city": "Hyderabad"
    }

    This changes customer 1's city to Hyderabad.
    """
    # Find the customer
    customer = None
    for c in customers_db:
        if c["id"] == customer_id:
            customer = c
            break

    if not customer:
        return {
            "status": "error",
            "message": f"Customer with ID {customer_id} not found"
        }

    # Update only the fields that were provided
    if update_data.name:
        customer["name"] = update_data.name
    if update_data.city:
        customer["city"] = update_data.city
    if update_data.risk:
        customer["risk"] = update_data.risk

    return {
        "status": "success",
        "message": "Customer updated successfully",
        "data": customer
    }


# ============================================================
# STEP 8: DELETE METHOD - Remove data
# ============================================================
# DELETE is used to REMOVE data.
# Example: Deleting an account, removing a post.
# ============================================================

@app.delete("/customer/{customer_id}")
def delete_customer(
    customer_id: int = Path(..., description="ID of customer to delete")
):
    """
    DELETE /customer/{customer_id}

    Deletes a customer from the database.

    Example: DELETE /customer/3
    This removes customer with ID 3.
    """
    global customers_db

    # Find the customer
    customer = None
    for c in customers_db:
        if c["id"] == customer_id:
            customer = c
            break

    if not customer:
        return {
            "status": "error",
            "message": f"Customer with ID {customer_id} not found"
        }

    # Remove from database
    customers_db = [c for c in customers_db if c["id"] != customer_id]

    return {
        "status": "success",
        "message": f"Customer '{customer['name']}' deleted successfully",
        "deleted_id": customer_id
    }




# ============================================================
# RUN INSTRUCTIONS
# ============================================================
# Save this file as main.py
# 
# Run the server with:
#   uvicorn main:app --reload
# 
# The --reload flag auto-restarts the server when you edit the file.
# 
# Visit these URLs in your browser:
#   http://127.0.0.1:8000/           -> Home
#   http://127.0.0.1:8000/docs       -> Interactive API docs (Swagger UI)
#   http://127.0.0.1:8000/redoc      -> Alternative docs (ReDoc)
# 
# Test with curl or Postman:
#   curl http://127.0.0.1:8000/customers
#   curl http://127.0.0.1:8000/customer/1
#   curl "http://127.0.0.1:8000/customers/filter?city=Bangalore&risk=high"
# 
# Test POST with curl:
#   curl -X POST "http://127.0.0.1:8000/customers" \
#        -H "Content-Type: application/json" \
#        -d '{"name":"Vikram","city":"Chennai","risk":"low"}'
# 
# Test ML Prediction:
#   curl -X POST "http://127.0.0.1:8000/predict" \
#        -H "Content-Type: application/json" \
#        -d '{"age":30,"income":500000,"city":"Bangalore"}'
# ============================================================
