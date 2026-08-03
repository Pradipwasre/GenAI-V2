# FastAPI Notes for Students

## Why Learn FastAPI

- FastAPI is a critical skill for Machine Learning Engineer roles
- India currently has 73,000+ openings for ML engineers, with salaries above Rs 12 lakh
- Many candidates fail interviews due to weak API/FastAPI skills
- API development and deployment are must have skills for ML jobs, not optional extras

## What is an API

- API stands for Application Programming Interface
- It is an agreement that lets two programs exchange data in a fixed format
- Example: a weather API takes a city name and returns temperature as JSON

## What is FastAPI

- FastAPI is a modern Python web framework used to build APIs
- It automatically handles data validation, documentation generation, and error handling
- It is fast, simple, and works well within the Python ecosystem

## Server and Client

- Server: accepts requests and sends back responses
- Client: sends requests to the server (example: your browser, laptop, or mobile app)

## HTTP Methods

| Method | Purpose | Example |
|--------|---------|---------|
| GET | Retrieve data | Viewing a web page |
| POST | Submit new data | Filling a form |
| PUT | Update existing data | Editing a profile |
| DELETE | Remove data | Deleting an account |

## JSON

- JSON stands for JavaScript Object Notation
- It is a lightweight data format understood by most programming languages
- It looks similar to a Python dictionary
- Used to exchange data between client and server in APIs

## URL and Endpoint

- URL: the address used to call an API (protocol + server address + endpoint)
- Endpoint: the specific URL that triggers an API function
- Example: `/predict` is an endpoint used for predictions

## Path Parameters

- Embedded directly inside the URL
- Used to identify a specific resource
- Example: `/customer/{customer_id}`
- `customer_id` is a dynamic value that changes with each request

## Query Parameters

- Added after a `?` at the end of the URL
- Used to filter or customize the response
- Example: `/customers?city=Bangalore&risk=high`
- This filters only high risk customers from Bangalore

## Path vs Query Parameters

- Path parameters: best for identifying one specific item
- Query parameters: best for filtering or customizing results on an endpoint

## Pydantic

- A Python library used for data validation
- Checks that incoming data matches the expected type and structure
- Example: if age is sent as text instead of a number, Pydantic raises a clear error
- Prevents bad data from crashing the API in production

## Error Handling

- Good APIs never crash, they return a clear error message instead
- FastAPI uses HTTPException to return proper status codes:
  - 400: Bad Request
  - 404: Not Found
  - 422: Unprocessable Entity
  - 500: Internal Server Error
- Three layers of protection:
  1. Pydantic auto validation
  2. Custom business logic checks (example: does this ID exist)
  3. try-except blocks for unexpected errors

## File Upload

- Real world ML models often need to process bulk data, usually as CSV files
- FastAPI can accept an uploaded file, parse it, and convert it into a pandas DataFrame
- The API should check that the file is a valid CSV and has the required columns
- Output can be returned as a downloadable CSV file
- This allows predictions on many records at once, instead of one at a time

## Case Study: California House Price Prediction API

### The Problem
- 5,000+ real estate agents were manually estimating house prices
- The process took 2 to 3 days per estimate
- Different agents gave different prices for the same house, confusing customers
- Only 10 expert evaluators were available, far less than the demand

### The Solution
- A Random Forest Regressor model was trained on 20,640 historical house records
- The trained model can estimate a price in seconds
- The model was deployed using FastAPI so it is available 24/7
- Any agent can now get an instant price online

### Key Metrics
- R2 Score: measures model performance (1.0 is perfect, 0.0 is poor)
- MAE (Mean Absolute Error): average error was around $32,760

## End to End Project Workflow

1. Data exploration and understanding
2. Train and test data split
3. Train the model (Random Forest Regressor)
4. Evaluate performance (MAE, R2 Score)
5. Save the trained model using joblib
6. Define an input schema using Pydantic
7. Build the API endpoint in FastAPI
8. Return predictions based on input parameters
9. Add error handling and file upload support

## Quick Recap

- API: agreement for programs to exchange data
- FastAPI: Python framework to build APIs quickly with built in validation
- GET, POST, PUT, DELETE: the four core HTTP methods
- Path parameter: identifies one resource, part of the URL
- Query parameter: filters or customizes results, comes after `?`
- Pydantic: validates data types and structure
- HTTPException: returns proper error codes and messages
- File upload: enables bulk predictions from a CSV file