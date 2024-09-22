from fastapi import FastAPI, Depends, Form, UploadFile, File, HTTPException
from database import SessionLocal
from fastapi.encoders import jsonable_encoder
import crud, schemas,models
import uvicorn
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
import os
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from fastapi import Body
from werkzeug.security import generate_password_hash, check_password_hash
#load_dotenv()


app = FastAPI()

origins = [
    "http://localhost:5173",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/online")
def online():
    return {"status": "OK"}

# Get all employees
@app.get("/employees", response_model=list[schemas.EmployeeResponse])
def get_all_employees(db: Session = Depends(get_db)):
    result = crud.get_employees(db)
    if result == []:
        raise HTTPException(status_code=404, detail="No employees found.")
    return jsonable_encoder(crud.get_employees(db))

# Create employee
@app.post("/employees")
async def create_employee(employee: schemas.Employee, db: Session = Depends(get_db)):
    result = crud.create_employee(db, employee)
    if not result:    
        raise HTTPException(status_code=409, detail="Employee already exists.")
    return result


# Get employee by name
@app.get("/employees/{name}", response_model=schemas.EmployeeResponse)
async def get_employee_by_name(name: str, db: Session = Depends(get_db)):
    result = crud.get_employee_by_name(db, name)
    if result is None:
        raise HTTPException(status_code=404, detail="Employee not found.")
    return jsonable_encoder(result)

@app.post("/signup")
def signup(employee: schemas.Employee):
    employee.password_hash = generate_password_hash(employee.password, method='pbkdf2:sha256')
    # signup code here

    return jsonable_encoder({"message": "User created successfully.", "user": user_result.json()})

@app.post("/login")
def login(login: schemas.Login):
    # login = email & password
    # login code here
    user_result = user_result.json()
    if not check_password_hash(user_result["password_hash"], login.password):
        raise HTTPException(status_code=401, detail="Invalid password.")
    return jsonable_encoder({"message": "User logged in successfully.", "user": user_result})

@app.post("/requests/")
def create_request(request: schemas.RequestCreate, db: Session = Depends(get_db)):
    db_request = models.Request(
        staff_id=request.staff_id,
        schedule_id=request.schedule_id,
        reason=request.reason,
        status=request.status,
        date=request.date,
        time_slot=request.time_slot,
        request_type=request.request_type,
    )
    
    db.add(db_request)
    db.commit()
    db.refresh(db_request)  
    
    return db_request


# Retrieve all staff IDs based on Team_ID (Logged in user's) and retrieve all their requests
@app.get("/team/{team_id}/requests", response_model=list[schemas.RequestResponse])
def get_requests_for_team(team_id: int, db: Session = Depends(get_db)):
    # Get all Staff_IDs by the specified Team_ID
    staff_ids = crud.get_staff_ids_by_team(db, team_id)
    
    # Check if staff_ids list is empty and throw error message if it is
    if not staff_ids:
        raise HTTPException(status_code=404, detail=f"No staff found for Team ID {team_id}")
    
    # Get all requests for the list of staff IDs
    requests = crud.get_requests_by_staff_ids(db, staff_ids)
    
    # Check if requests are found, else throw error message
    if not requests:
        raise HTTPException(status_code=404, detail="No requests found for staff members in this team.")
    
    # Return the retrieved request records
    return jsonable_encoder(requests)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5049)