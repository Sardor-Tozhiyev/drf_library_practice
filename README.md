# Library API

A RESTful API for managing a library system built with Django REST Framework.

The application provides authentication, book management, borrowing management, overdue notifications, payment integration, API documentation, automated tests, and Docker support.

## Features

* User registration and authentication
* JWT authentication
* Custom user model with email-based authentication
* Book management
* Borrowing management
* Inventory management
* Automatic inventory updates when books are borrowed or returned
* Borrowing due-date tracking
* Overdue borrowing detection
* Fine calculation for overdue borrowings
* Payment session creation
* Telegram notifications
* Background task processing with Django-Q
* Filtering and pagination
* Swagger / OpenAPI documentation
* Automated tests
* Test coverage reporting
* Docker and Docker Compose support
* PostgreSQL database support

## Tech Stack

* Python 3.13
* Django
* Django REST Framework
* PostgreSQL
* Simple JWT
* drf-spectacular
* Django-Q
* Docker
* Docker Compose
* Coverage.py
* Telegram Bot API

## Project Structure

```text
drf_library_practice/
├── borrowings_service/
│   ├── migrations/
│   ├── tests.py
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
│
├── books_service/
│   ├── migrations/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
│
├── users_service/
│   ├── migrations/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
│
├── services/
│   └── payment / notification related services
│
├── drf_library_practice/
│   ├── settings.py
│   ├── urls.py
│   └── ...
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── manage.py
└── README.md
```

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd drf_library_practice
```

### 2. Configure environment variables

Create a `.env` file based on the provided `.env.sample`:

```bash
cp .env.sample .env
```

Configure the required environment variables.

Example:

```env
POSTGRES_DB=library
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=db
POSTGRES_PORT=5432

DJANGO_SECRET_KEY=your_secret_key
DJANGO_DEBUG=True

TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

PAYMENT_SUCCESS_URL=http://localhost:8000/
PAYMENT_CANCEL_URL=http://localhost:8000/
```

Do not commit `.env` or other files containing real credentials to the repository.

## Running with Docker

The recommended way to run the project is with Docker Compose.

Build the containers:

```bash
docker compose build
```

Start the application:

```bash
docker compose up
```

Or run it in detached mode:

```bash
docker compose up -d
```

The application will be available at:

```text
http://localhost:8000/
```

## Database

Run migrations:

```bash
docker compose exec library python manage.py migrate
```

Create a superuser:

```bash
docker compose exec library python manage.py createsuperuser
```

If the project contains fixtures, they can be loaded with:

```bash
docker compose exec library python manage.py loaddata <fixture_name>
```

## API Documentation

The project uses `drf-spectacular` to generate an OpenAPI schema and Swagger documentation.

Swagger UI:

```text
http://localhost:8000/api/schema/swagger-ui/
```

OpenAPI schema:

```text
http://localhost:8000/api/schema/
```

The Swagger interface can be used to explore available endpoints, request parameters, serializers, authentication requirements, and response schemas.

## Authentication

The API uses JWT authentication.

Typical authentication flow:

1. Register a user.
2. Obtain JWT access and refresh tokens.
3. Include the access token in authenticated requests.

Authorization header:

```http
Authorization: Bearer <access_token>
```

JWT endpoints:

```text
/api/users/token/
/api/users/token/refresh/
```

The exact endpoint paths are documented in Swagger.

## Books

The books API provides functionality for managing the library inventory.

Typical operations include:

* List books
* Retrieve a book
* Create a book
* Update a book
* Delete a book
* Filter books
* Paginate book results

Access permissions depend on the user's authentication and staff status.

## Borrowings

Borrowings allow authenticated users to borrow and return books.

The borrowing functionality includes:

* Creating a borrowing
* Viewing borrowing history
* Returning books
* Tracking borrowing dates
* Tracking expected return dates
* Updating book inventory
* Detecting overdue borrowings
* Creating fines for overdue returns

When a borrowing is created, the available inventory of the selected book is decreased.

When a book is returned, the inventory is restored.

## Overdue Borrowings

The project contains a management command for checking overdue borrowings:

```bash
docker compose exec library python manage.py check_overdue_borrowings
```

The command checks overdue borrowings and performs the required notification/payment-related actions.

Example output:

```text
Checked overdue borrowings. Notified: 0
```

## Background Tasks

Django-Q is used for background task processing.

This allows operations such as notifications and scheduled jobs to be executed asynchronously without blocking API requests.

The Django-Q configuration is included in the project settings and Docker environment.

## Telegram Notifications

The project can send Telegram notifications for relevant library events, such as overdue borrowings.

Telegram configuration is provided through environment variables:

```env
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

The bot credentials should never be committed to the repository.

## Payments

The application supports creating payment sessions for borrowing-related payments and fines.

Payment configuration is provided through environment variables.

Payment logic is isolated from the API views to keep the application structure maintainable and easier to test.

## API Testing

Run the complete test suite inside the Docker container:

```bash
docker compose exec library python manage.py test
```

To run tests for a specific application:

```bash
docker compose exec library python manage.py test borrowings_service
```

The test suite covers important application functionality including:

* Models
* Serializers
* API endpoints
* Borrowing creation
* Inventory changes
* Book returns
* Overdue borrowings
* Fine creation
* Payment session integration

External services are mocked in tests where appropriate.

## Test Coverage

Coverage.py is used to measure test coverage.

Run tests with coverage:

```bash
docker compose exec library coverage run --source=. manage.py test
```

Display the coverage report:

```bash
docker compose exec library coverage report -m
```

Generate an HTML coverage report:

```bash
docker compose exec library coverage html
```

The generated report will be available in:

```text
htmlcov/index.html
```

## Code Quality

The project follows common Python and Django code quality practices.

Before committing changes, it is recommended to run:

```bash
ruff check .
```

and the test suite:

```bash
docker compose exec library python manage.py test
```

## Django Management Commands

Available custom management commands include:

### Check overdue borrowings

```bash
docker compose exec library python manage.py check_overdue_borrowings
```

This command checks borrowing records for overdue items and processes the corresponding notifications and fines.

## Docker Services

The project uses Docker Compose to run the required services.

Typical services include:

* Django application
* PostgreSQL database
* Background task worker

The database is isolated in its own Docker container, while the Django application communicates with it through the Docker Compose network.

## Environment Variables

The project uses environment variables for configuration and sensitive information.

Important variables include:

| Variable             | Description                    |
| -------------------- | ------------------------------ |
| `DJANGO_SECRET_KEY`  | Django secret key              |
| `DJANGO_DEBUG`       | Debug mode                     |
| `POSTGRES_DB`        | PostgreSQL database name       |
| `POSTGRES_USER`      | PostgreSQL username            |
| `POSTGRES_PASSWORD`  | PostgreSQL password            |
| `POSTGRES_HOST`      | PostgreSQL host                |
| `POSTGRES_PORT`      | PostgreSQL port                |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token             |
| `TELEGRAM_CHAT_ID`   | Telegram chat ID               |
| Payment variables    | Payment provider configuration |

Use `.env.sample` as a template for local configuration.

## Development Workflow

A typical development workflow:

```bash
docker compose up -d
```

Run migrations:

```bash
docker compose exec library python manage.py migrate
```

Run tests:

```bash
docker compose exec library python manage.py test
```

Check code quality:

```bash
ruff check .
```

Check coverage:

```bash
docker compose exec library coverage run --source=. manage.py test
docker compose exec library coverage report -m
```

## API Architecture

The project follows a modular Django REST Framework architecture.

Main responsibilities are separated between:

* **Models** — database structure and business data
* **Serializers** — validation and API representation
* **Views / ViewSets** — API request handling
* **Permissions** — access control
* **Services** — integrations with external systems
* **Management commands** — scheduled or administrative operations
* **Tests** — automated verification of application behavior

This structure makes the project easier to maintain, test, and extend.

## Security

Sensitive configuration is stored in environment variables and should not be committed to version control.

In production environments:

* Set `DEBUG=False`
* Use a strong Django secret key
* Use secure database credentials
* Configure HTTPS
* Restrict allowed hosts
* Protect payment and Telegram credentials
* Do not expose sensitive environment variables

## License

This project was created for educational and backend development practice purposes.
