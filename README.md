# Smart Shift Optimizer & Fatigue Tracker

A FastAPI-based application designed to manage and intelligently assign employees to tasks. This project features a role-based authentication system, persistent data storage with MySQL, and a sophisticated algorithm for task allocation that considers employee skills, availability, and real-time fatigue levels.

---

## ✨ Features

* **Role-Based Access Control**: Secure endpoints distinguish between **Manager** and **Employee** roles. Managers can add staff and assign tasks, while employees can view their own status.
* **Token-Based Authentication**: Uses JWT (JSON Web Tokens) for secure, stateless authentication.
* **Intelligent Task Assignment**: Automatically assigns the best-suited employees to tasks based on a robust set of rules.
* **Dynamic Fatigue Calculation**: A system to track and update employee fatigue in real-time based on workload and shift history.
* **Persistent Database**: Leverages MySQL with a SQLAlchemy ORM for all data storage.

---

## 🛠️ Technologies Used

* **Backend**: Python, FastAPI
* **Security**: JWT, Passlib, BCrypt
* **Database**: MySQL
* **ORM**: SQLAlchemy
* **Data Validation**: Pydantic

---

## 🚀 Getting Started

### Prerequisites

* Python 3.10+
* MySQL Server

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
    *Create a `requirements.txt` file and add `fastapi`, `uvicorn`, `sqlalchemy`, `pymysql`, `python-dotenv`, `passlib[bcrypt]`, `python-jose`, and `cryptography`. Then run:*
    ```sh
    pip install -r requirements.txt
    ```
4.  **Set up your environment variables:**
    * Create a `.env` file in the root directory. This file is listed in the `.gitignore` and will not be committed.
    * Add your database and security credentials:
        ```ini
        # Database Credentials
        DB_HOST=localhost
        DB_USER=your_user
        DB_PASSWORD="your_password"
        DB_NAME=your_db_name

        # Security Credentials
        SECRET_KEY="a-very-strong-and-super-secret-key"
        HASHING_ALGORITHM="HS256"
        ```
5.  **Run the application:**
    ```sh
    uvicorn main:app --reload
    ```
    
    The API will be available at `http://127.0.0.1:8000`. You can view the interactive documentation at `http://127.0.0.1:8000/docs`.

6.  **Test the API:**
    * Navigate to **`http://127.0.0.1:8000/docs`** in your browser.
    * This will open the interactive Swagger UI where you can test all the API endpoints directly. No external client is needed.



---

## 🔐 Authentication Flow

1.  **Register First Manager**: The very first user to be created via the `/register` endpoint is automatically assigned the `'manager'` role.
2.  **Login to Get Token**: Any user (manager or employee) sends their `username` and `password` to the `/token` endpoint to receive a JWT access token.
3.  **Authorize Requests**: To access protected endpoints, include the token in the request header: `Authorization: Bearer <your_token>`.

---

## ⚙️ API Endpoints

### Public Endpoints

* **`POST /register`**: Creates a new user. The first user becomes a manager; all others become employees.
* **`POST /token`**: Exchanges a username and password for a JWT access token.

### User Endpoints (Employee & Manager)

* **`GET /users/me`**: Fetches the details for the currently authenticated user.

### Manager-Only Endpoints

* **`POST /employees`**: Allows a manager to add a new employee or another manager to the system.
* **`GET /employees`**: Fetches a list of all employees.
* **`POST /task`**: Submits a new task, triggers the assignment logic, and returns the list of assigned employees.

---

## 🗺️ Roadmap (Tasks to Complete)

* **Enhanced Validation & Edge Case Handling**:
    * Add robust error handling for all request bodies.
    * Gracefully handle edge cases, such as assigning tasks in the past or providing an invalid number of members.
* **Code Optimization**:
    * Refactor business logic to improve performance, especially in the task assignment algorithm.
    * Optimize database queries to reduce load and response times.
* **Dockerization**:
    * Create a `Dockerfile` and `docker-compose.yml` to containerize the application for easy deployment.
* **Additional Endpoints**:
    * Introduce `PUT` and `DELETE` endpoints for more flexible data management.