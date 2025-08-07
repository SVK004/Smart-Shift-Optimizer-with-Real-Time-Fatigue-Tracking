Workforce Management API

A FastAPI-based application designed to manage and intelligently assign employees to tasks based on their skills, availability, and a dynamic fatigue calculation system. This project ensures optimal task allocation by minimizing employee fatigue and preventing overwork.

---> Features
RESTful API: Full CRUD (Create, Read, Update, Delete) capabilities for managing employees and tasks.

Intelligent Task Assignment: Automatically assigns the best-suited employees to a task based on a sophisticated set of rules.

Dynamic Fatigue Calculation: A system to track and update employee fatigue in real-time. Fatigue is calculated based on:

Hours worked within a recent period.

Total hours worked against their weekly maximum.

Time between consecutive shifts.

Database Integration: Uses MySQL with SQLAlchemy ORM for persistent data storage.

---> Technologies Used
Backend: Python, FastAPI

Database: MySQL

ORM: SQLAlchemy

Data Validation: Pydantic


API Endpoints

Employees
GET /employees: Fetches a list of all employees.

GET /employees/{id}: Fetches details for a single employee by their ID.

POST /employees: Adds a new employee to the system.

Tasks
POST /task: Submits a new task, triggers the assignment logic, and returns the list of assigned employees.

---------------------------------------------------------------------------------------------------------------------------------------------------

---> Tasks to Complete
Enhanced Validation: Add robust error handling and validation for all request bodies to prevent bad data.

Edge Case Handling: Improve logic to gracefully handle edge cases, such as:

Attempting to assign tasks in the past.

Invalid number of members requested for a task.

Code Refactoring: Refactor business logic to improve performance and reduce code repetition.

Additional Endpoints: Introduce new endpoints for more flexible data management (e.g., updating tasks, managing employee skills separately).