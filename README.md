# Flask Web Application with Celery and PostgreSQL

This project is a Flask web application integrated with Celery for asynchronous task processing and PostgreSQL for database management. It features user authentication, file upload, and data processing functionalities.

## Features

- User authentication (login/signup)
- File upload and processing with Celery
- Data management with PostgreSQL
- Query builder and result display

## Prerequisites

- Python 3.9+
- PostgreSQL
- Redis (for Celery)
- Virtual Environment

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/your-repo.git
   cd your-repo

2. **Setup Virtual Environment**
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`

3. **Install Dependencies**
    pip install -r requirements.txt

4. **Configure Environment Variable**
    to configure your PostgreSQL and Redis settings. Create a `.env` file in the root directory of the project with the following content (replace placeholders with your actual values):

    '''
    SECRET_KEY=your_secret_key
    SQLALCHEMY_DATABASE_URI=postgresql://username:password@localhost/dbname
    CELERY_BROKER_URL=redis://127.0.0.1:6379/0
    CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/0
    '''

5. **Initialize Database**
    `flask db upgrade`


## Running the Application

1. **Running Redis Server**
    `redis-server`

2. **Start Celery Worker**
    `celery -A run.celery worker --loglevel=info` 
    if using on windows run it with below code if its not working as expected
    `celery -A run.celery worker --loglevel=info -P solo`

3. **Run Flask App**
    `py or python app.py`


## Usage
    Landing Page: Visit http://127.0.0.1:8001/ for the landing page.
    Login: Access the login page at http://127.0.0.1:8001/login.
    Signup: Access the signup page at http://127.0.0.1:8001/signup.
    Upload Data: Navigate to http://127.0.0.1:8001/upload_data to upload CSV files for processing.
    Manage Users: View user data at http://127.0.0.1:8001/users.
    Query Builder: Build and execute queries at http://127.0.0.1:8001/query_builder.




### Notes:
- **Replace placeholders**: Make sure to replace placeholders like `yourusername`, `your-repo`, and `your_secret_key` with your actual details.
- **Database and Redis Configuration**: Ensure that your PostgreSQL and Redis configurations match your actual setup.
- **Celery Worker**: Adjust the `celery -A run.celery worker` command if your module name or Celery configuration is different.
