# Smart Shift Optimizer & Fatigue Tracker

A sophisticated FastAPI application for workforce management, featuring a three-tier, role-based security model (`supermanager`, `manager`, `employee`). This project is fully containerized with Docker, uses a persistent MySQL backend, and leverages an intelligent algorithm to assign tasks based on employee skills, availability, and real-time fatigue levels.

---

## ✨ Features

* **Three-Tier Role-Based Access Control**:
    * **Supermanager (Admin)**: The system administrator, responsible for registering all new users.
    * **Manager**: Manages day-to-day operations, including assigning tasks and viewing employee data.
    * **Employee**: Can view their own status and task schedule.
* **Token-Based Authentication**: Uses JWT (JSON Web Tokens) for secure, stateless authentication.
* **Intelligent Task Assignment**: Automatically assigns the best-suited employees to tasks based on a robust set of rules.
* **Dynamic Fatigue Calculation**: A system to track and update employee fatigue in real-time based on workload and shift history.
* **Fully Containerized**: Packaged with Docker and Docker Compose for easy setup and deployment.

---

## 🛠️ Technologies Used

* **Backend**: Python, FastAPI
* **Containerization**: Docker, Docker Compose
* **Security**: JWT, Passlib, BCrypt
* **Database**: MySQL
* **ORM**: SQLAlchemy
* **Testing**: Pytest

---

## 🚀 Getting Started with Docker

### Prerequisites

* Docker and Docker Compose

### Installation & Setup

1.  **Clone the repository:**
    ```sh
    git clone <your-repository-url>
    cd smart-shift-optimizer-with-real-time-fatigue-tracking
    ```
2.  **Create `requirements.txt`:**
    * Create a `requirements.txt` file and add all necessary packages (`fastapi`, `uvicorn`, `sqlalchemy`, `pymysql`, `python-dotenv`, `passlib[bcrypt]`, `python-jose`, `cryptography`, `python-multipart`).

3.  **Set up your Environment Variables:**
    * Create a `.env` file in the root directory. This file is listed in the `.gitignore` and will not be committed.
    * Add your database and security credentials. **Ensure `DB_HOST` is set to `db` for Docker networking.**
        ```ini
        # For the MySQL Container
        MYSQL_ROOT_PASSWORD="a_very_strong_root_password"
        MYSQL_DATABASE="your_db_name"
        MYSQL_USER="app_user"
        MYSQL_PASSWORD="app_password"

        # For the FastAPI App
        DB_HOST=db
        DB_NAME="your_db_name"
        DB_USER="app_user"
        DB_PASSWORD="app_password"

        # For Security
        SECRET_KEY="a-very-strong-and-super-secret-key"
        HASHING_ALGORITHM="HS256"
        ```
4.  **Build and Run the Containers:**
    ```sh
    docker-compose up --build -d
    ```
5.  **Access the API:**
    * The API will be available at `http://localhost:8000`.
    * Navigate to **`http://localhost:8000/docs`** in your browser to use the interactive Swagger UI.

---

## 🔐 Authentication Flow & User Roles

This system has a specific setup flow to ensure security.

1.  **Create the Supermanager**: The very first user created via the `/register` endpoint is automatically assigned the `'supermanager'` role. **This should only be done once.**
2.  **Supermanager Registers Other Users**: The Supermanager logs in via `/token` to get an access token. They then use this token to access the `/register` endpoint to create all other `manager` and `employee` accounts.
3.  **Manager and Employee Login**: Once created, managers and employees can log in via `/token` to get their own access tokens to access the endpoints permitted for their roles.

---

## ⚙️ API Endpoints

### Supermanager-Only Endpoints

* **`POST /register`**: Creates a new user (`manager` or `employee`). Can only be accessed by the `supermanager`.

### Public Endpoint

* **`POST /token`**: Exchanges a username and password for a JWT access token. Accessible by all roles.

### User Endpoints (Employee & Manager)

* **`GET /users/me`**: Fetches the details for the currently authenticated user.

### Manager-Only Endpoints

* **`POST /employees`**: Allows a manager to add a new employee or another manager to the system.
* **`GET /employees`**: Fetches a list of all employees.
* **`POST /task`**: Submits a new task, triggers the assignment logic, and returns the list of assigned employees.

---

## 🧪 How to Run Tests

1.  **Set up Test Database**: Add a `TEST_DB_URL` variable to your `.env` file pointing to a separate, empty test database.
    ```ini
    TEST_DB_URL="mysql+pymysql://user:password@localhost/test_db_name"
    ```
2.  **Install Test Dependencies**:
    ```sh
    pip install pytest httpx
    ```
3.  **Run Pytest**: From your project's root directory, run the command:
    ```sh
    pytest -v
    ```

---

## 🗺️ Roadmap

* **Enhanced Validation**: Add more robust error handling for all request bodies.
* **Code Optimization**: Refactor business logic to improve performance.
* **Additional Endpoints**: Introduce `PUT` and `DELETE` endpoints for more flexible data management.
