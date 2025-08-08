# Smart Shift Optimizer & Fatigue Tracker

A FastAPI-based application designed to manage and intelligently assign employees to tasks based on their skills, availability, and a dynamic fatigue calculation system. This project ensures optimal task allocation by minimizing employee fatigue and preventing overwork, using a persistent MySQL backend.

---

## ✨ Features

* **RESTful API**: Full capabilities for managing employees and tasks, including creating, reading, and assigning.
* **Intelligent Task Assignment**: Automatically assigns the best-suited employees to a task based on a sophisticated set of rules, including skill matching and current fatigue levels.
* **Dynamic Fatigue Calculation**: A system to track and update employee fatigue in real-time. Fatigue is calculated based on:
    * Hours worked within a recent period.
    * Total hours worked against their weekly maximum.
    * Time between consecutive shifts.
* **Database Integration**: Uses MySQL with SQLAlchemy ORM for persistent data storage.

---

## 🛠️ Technologies Used

* **Backend**: Python, FastAPI
* **Database**: MySQL
* **ORM**: SQLAlchemy
* **Data Validation**: Pydantic

---

## 🚀 Getting Started

### Prerequisites

* Python 3.10+
* MySQL Server
* An API client like [Postman](https://www.postman.com/) (optional)

### Installation & Setup

1.  **Clone the repository:**
    ```sh
    git clone <your-repository-url>
    cd smart-shift-optimizer-with-real-time-fatigue-tracking
    ```
2.  **Create and activate a virtual environment:**
    ```sh
    # On macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # On Windows
    python -m venv venv
    venv\Scripts\activate
    ```
3.  **Install the required packages:**
    *Create a `requirements.txt` file with the necessary packages (FastAPI, Uvicorn, SQLAlchemy, PyMySQL, python-dotenv, cryptography) and run:*
    ```sh
    pip install -r requirements.txt
    ```
4.  **Set up your environment variables:**
    * Create a `.env` file in the root directory. This file is listed in the `.gitignore` and will not be committed.
    * Add your database credentials to the `.env` file:
        ```ini
        DB_HOST=localhost
        DB_USER=your_user
        DB_PASSWORD="your_password"
        DB_NAME=your_db_name
        ```
5.  **Run the application:**
    ```sh
    uvicorn main:app --reload
    ```
    The API will be available at `http://127.0.0.1:8000`. You can view the interactive documentation at `http://127.0.0.1:8000/docs`.

---

## ⚙️ API Endpoints

### Employees

* **`GET /employees`**: Fetches a list of all employees.
* **`GET /employees/{id}`**: Fetches details for a single employee by their ID.
* **`POST /employees`**: Adds a new employee to the system.

### Tasks

* **`POST /task`**: Submits a new task, triggers the assignment logic, and returns the list of assigned employees.

---

## 🗺️ Roadmap (Tasks to Complete)

* **Enhanced Validation & Edge Case Handling**:
    * Add robust error handling and validation for all request bodies to prevent bad data.
    * Improve logic to gracefully handle edge cases, such as attempting to assign tasks in the past or providing an invalid number of members.
* **Code Optimization**:
    * Refactor business logic to improve performance, especially in the task assignment algorithm.
    * Optimize database queries to reduce load and response times.
* **Dockerization**:
    * Create a `Dockerfile` and `docker-compose.yml` to containerize the FastAPI application and the MySQL database for easy deployment and development setup.
* **Additional Endpoints**:
    * Introduce new endpoints for more flexible data management (e.g., `PUT` to update tasks, `DELETE` to remove employees, etc.).