- User authentication (Student, Librarian roles)
- API endpoints for managing books, users, and checkouts.
- Swagger UI for API documentation and testing.
- Search and filtering for books.
- Environment-based configuration using a `.env` file.

## Setup and Installation

1.  **Clone the repository** (or navigate into the `backend` directory if you already have it).

2.  **Create the Environment File:**
    Inside the `backend` directory, create a file named `.env` and add your configuration variables. This file is ignored by version control and should contain your secrets.
    ```.env
    # backend/.env
    SECRET_KEY='your-super-secret-key-here'
    DEBUG=True
    DATABASE_URL='postgres://user:password@localhost:5432/ulibrary_db'
    CORS_ALLOWED_ORIGINS="http://localhost:3000,http://127.0.0.1:3000"
    ```
    **Note:** The project's `settings.py` needs to be configured to read this file (e.g., using `python-dotenv`). You should also add `.env` to your `.gitignore` file to keep secrets out of version control.

3.  **Create a virtual environment and activate it:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

4.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Generate Initial Migrations:**
    Run `makemigrations` to create the migration files based on the models defined in your `library` app. This command should be run whenever you make changes to your `models.py` file.
    ```bash
    python manage.py makemigrations
    ```

6.  **Apply Migrations to the Database:**
    Run the `migrate` command to apply the migrations to your database, creating or updating the necessary tables.
    ```bash
    python manage.py migrate
    ```

8.  **(Optional) Seed the Database:**
    To populate the database with sample data, run the `seed_data` command. You can specify the number of records to create.
    ```bash
    # Create 200 books and 50 users
    python manage.py seed_data

    # Clear existing data and create 500 books and 100 users
    python manage.py seed_data --books 500 --users 100 --clear
    ```

7.  **Create a superuser (Librarian):**
    Follow the prompts to create a librarian account. When creating users via the API, you can set their role.
    ```bash
    python manage.py createsuperuser
    ```

8.  **Run the development server:**
    Use `runserver_plus` from the `django-extensions` library. This provides a superior development server that automatically reloads when you change any project file. I've renumbered this step.
    ```bash
    python manage.py runserver_plus
    ```

## API Documentation

Once the server is running, the root URL `http://127.0.0.1:8000/` will automatically redirect to the Swagger UI for interactive API documentation.

You can also access:
- **ReDoc:** `http://127.0.0.1:8000/api/schema/redoc/`

## Running Tests

The project includes a comprehensive test suite. To run the tests, use the following command from the `backend` directory:
```bash
python manage.py test
```

## Building with Cython (Optional)

This project includes an optional build step using Cython to compile parts of the Python code into C extensions for a potential performance increase. To compile the modules, run the following command from the `backend` directory:
```bash
python setup.py build_ext --inplace
```
---

## Development Environments

You can run this project in two ways: locally using a virtual environment, or containerized using Docker.

### Local Development (without Docker)

Follow the steps in the "Setup and Installation" section above. This requires you to have Python and PostgreSQL installed on your local machine. Your `.env` file should point to your local PostgreSQL instance (e.g., `DATABASE_URL='postgres://user:pass@localhost:5432/dbname'`).

### Containerized Development (with Docker)

The project is configured to run the full stack (Django backend, React frontend, and PostgreSQL database) using Docker Compose for a consistent development environment.

1.  **Ensure Docker is installed** on your system.
2.  **Create Docker Environment File:** Create a file named `.env.docker` in the `backend` directory. This file will override settings from `.env` for the containerized environment.
    ```.env
    # backend/.env.docker
    DATABASE_URL=postgres://username:database_password@db_name:5432/ulibrary_db # Connects backend to db service
    POSTGRES_DB=<database_name>
    POSTGRES_USER=<database_username>
    POSTGRES_PASSWORD=<database_password>
    ```
3.  **Build and run the containers:** From the `backend` directory, run the following command. This will build and start all services.
    ```bash
    docker-compose up --build
    ```
    This command will build the images for the frontend and backend, pull the PostgreSQL image, and start all services.
    - The **React Frontend** will be available at `http://localhost:3000`.
    - The **Django API** will be available at `http://localhost:8000`.
