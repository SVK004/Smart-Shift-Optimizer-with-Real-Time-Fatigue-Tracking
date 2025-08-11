from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from models import Employee as DBEmployee

# Test Case 1: Successful Manager Registration and Login
def test_register_and_login_manager(client: TestClient):

    response = client.post(
        "/register",
        json={
            "name": "TestManager",
            "availability": [],
            "skills": ["Management"],
            "maxWeeklyHours": 40,
            "password": "managerpassword"
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["role"] == "manager"


    login_response = client.post(
        "/token",
        data={"username": "TestManager", "password": "managerpassword"},
    )
    assert login_response.status_code == 200
    token_data = login_response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"



# Test Case 2: Manager Successfully Adds an Employee
def test_manager_adds_employee(client: TestClient):
    """
    Tests a manager's ability to add a new employee.
    Requires a manager to exist, so we create one first.
    """
    # Step 1: Create a manager to perform the action
    client.post("/register", json={"name": "ManagerUser", "password": "password", "skills": [], "maxWeeklyHours": 40, "availability": []})
    login_res = client.post("/token", data={"username": "ManagerUser", "password": "password"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    employee_data = {
        "name": "NewDev",
        "availability": ["2025-01-01", "2025-12-31"],
        "skills": ["Python"],
        "maxWeeklyHours": 40,
        "password": "devpassword",
        "role": "employee"
    }
    response = client.post("/employees", json=employee_data, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "NewDev"
    assert data["role"] == "employee"

# Test Case 3: Employee Fails to Access a Manager-Only Endpoint
def test_employee_cannot_access_manager_route(client: TestClient):

    client.post("/register", json={"name": "TestManager", "password": "pw1", "skills": [], "maxWeeklyHours": 40, "availability": []})
    client.post("/register", json={"name": "TestEmployee", "password": "pw2", "skills": [], "maxWeeklyHours": 40, "availability": []})
    
    login_res = client.post("/token", data={"username": "TestEmployee", "password": "pw2"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/employees", headers=headers)
    assert response.status_code == 403
    assert response.json()["detail"] == "Not enough permissions"



# Test Case 4 (Edge Case): Task Allocation Fails When No Suitable Employee Exists
def test_task_allocation_fails_with_no_suitable_employees(client: TestClient):

    client.post("/register", json={"name": "Manager", "password": "pw", "skills": [], "maxWeeklyHours": 40, "availability": []})
    login_res = client.post("/token", data={"username": "Manager", "password": "pw"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    task_data = {
        "skills": ["QuantumComputing"],
        "time": "2025-10-10T09:00:00",
        "hoursRequired": 8,
        "members": 1
    }
    response = client.post("/task", json=task_data, headers=headers)
    assert response.status_code == 409
    assert response.json()["detail"] == "Not suitable employees..."



# Test Case 5 (Edge Case): Registration Fails for a Duplicate Username
def test_register_duplicate_username_fails(client: TestClient):

    user_data = {"name": "DuplicateUser", "password": "pw1", "skills": [], "maxWeeklyHours": 40, "availability": []}
    response1 = client.post("/register", json=user_data)
    assert response1.status_code == 201

    user_data_2 = {"name": "DuplicateUser", "password": "pw2", "skills": [], "maxWeeklyHours": 40, "availability": []}
    response2 = client.post("/register", json=user_data_2)
    assert response2.status_code == 400
    assert response2.json()["detail"] == "A user with this name already exists."



# Test Case 6: Successful Task Allocation
def test_successful_task_allocation(client: TestClient):

    client.post("/register", json={"name": "ManagerForTask", "password": "pw", "skills": [], "maxWeeklyHours": 40, "availability": []})
    client.post(
        "/register",
        json={
            "name": "PythonDev",
            "availability": ["2025-01-01", "2025-12-31"],
            "skills": ["Python", "SQL"],
            "maxWeeklyHours": 10,
            "password": "devpw"
        }
    )
    
    login_res = client.post("/token", data={"username": "ManagerForTask", "password": "pw"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    task_data = {
        "skills": ["Python"],
        "time": "2025-10-10T09:00:00",
        "hoursRequired": 8,
        "members": 1
    }
    response = client.post("/task", json=task_data, headers=headers)

    assert response.status_code == 200
    allotted_employees = response.json()
    assert len(allotted_employees) == 1
    assert allotted_employees[0]["name"] == "PythonDev"
    assert allotted_employees[0]["hoursWorked"] == 8.0


# Test Case 7 (Edge Case): Employee Rejected if Fatigue Goes Above 4
def test_employee_rejected_due_to_high_fatigue(client: TestClient, db_session: Session):

    client.post("/register", json={"name": "ManagerForFatigueTest", "password": "pw", "skills": [], "maxWeeklyHours": 40, "availability": []})
    client.post(
        "/register",
        json={
            "name": "TiredDev",
            "availability": ["2025-01-01", "2025-12-31"],
            "skills": ["Python"],
            "maxWeeklyHours": 10,
            "password": "devpw"
        }
    )
    
    login_res = client.post("/token", data={"username": "ManagerForFatigueTest", "password": "pw"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    first_task = {"skills": ["Python"], "time": "2025-10-01T09:00:00", "hoursRequired": 8, "members": 1}
    client.post("/task", json=first_task, headers=headers)


    tired_dev = db_session.query(DBEmployee).filter(DBEmployee.name == "TiredDev").first()
    tired_dev.fatigue = 2
    db_session.commit()
    db_session.refresh(tired_dev)
    

    second_task = {
        "skills": ["Python"],
        "time": "2025-10-02T09:00:00",
        "hoursRequired": 4,
        "members": 1
    }
 
    response = client.post("/task", json=second_task, headers=headers)

    assert response.status_code == 409
    assert response.json()["detail"] == "Not suitable employees..."