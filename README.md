# Bank API Demo

A FastAPI banking API backed by PostgreSQL. Docker Compose runs PostgreSQL, the API, and an NGINX gateway; the API can also be run directly on your machine with a local PostgreSQL server.

## Prerequisites

- Python 3.13
- PostgreSQL 16 for running the API without Docker
- Docker Desktop with Docker Compose v2 for the containerized setup and integration tests
- OpenSSL for generating the local HTTPS certificate used by NGINX

## Run with Docker

1. Copy the example environment file and set a private JWT secret and database credentials:

   ```sh
   cp .env.example .env
   ```

   Edit `.env` as needed. Compose reads this file to configure PostgreSQL and the API. Do not commit real credentials.

2. Generate a local self-signed certificate if `certs/server.crt` and `certs/server.key` are not already present. These files are intentionally excluded from Git:

   ```sh
   mkdir -p certs
   openssl req -x509 -nodes -newkey rsa:2048 \
     -keyout certs/server.key \
     -out certs/server.crt \
     -days 365 \
     -subj "/CN=localhost" \
     -addext "subjectAltName=DNS:localhost,IP:127.0.0.1"
   ```

3. Build and start the services. The API container applies Alembic migrations before starting:

   ```sh
   docker compose up --build -d
   ```

4. Check the API and open its documentation:

   ```sh
   curl -k https://localhost:8443/api/health
   ```

   The health response should be `{"status":"ok"}`. Swagger UI is at <https://localhost:8443/api/docs>. NGINX also listens on HTTP port `8000`; HTTPS is on port `8443`.

5. View service logs or stop the stack:

   ```sh
   docker compose logs -f
   docker compose down
   ```

`docker compose down` preserves the PostgreSQL volume. To remove the database volume as well, use `docker compose down -v`.

## Run without Docker

This runs FastAPI directly, but still requires a local PostgreSQL server and database.

1. Start PostgreSQL and create a database. For example, on a local PostgreSQL installation whose role matches your macOS username:

   ```sh
   createdb bankapidb
   ```

   Otherwise, create a PostgreSQL role and database using your installation's administration tools.

2. Create and activate a virtual environment, then install the application dependencies:

   ```sh
   python3.13 -m venv .venv
   source .venv/bin/activate
   python -m pip install -r requirements.txt
   ```

3. Set the database URL to match your local PostgreSQL role, password, host, and database. Set a private JWT signing key as well:

   ```sh
   export DATABASE_URL="postgresql+psycopg2://YOUR_DB_USER:YOUR_DB_PASSWORD@localhost:5432/bankapidb"
   export JWT_SECRET_KEY="replace-with-a-long-random-secret"
   ```

   If your PostgreSQL role has no password, omit `:YOUR_DB_PASSWORD` from the URL. The application also loads variables from a local `.env` file.

4. Apply migrations and start the development server:

   ```sh
   alembic upgrade head
   uvicorn main:app --reload
   ```

   The API is available at <http://127.0.0.1:8000>, its health endpoint is <http://127.0.0.1:8000/health>, and Swagger UI is at <http://127.0.0.1:8000/docs>.

## Run the tests

The tests are integration tests: they send HTTPS requests through the NGINX gateway to the running API. Start a test stack first; do not point them at a production database.

1. Create the test environment file if needed, then install the test dependencies:

   ```sh
   cp .env.example .env.test
   python3.13 -m venv .venv
   source .venv/bin/activate
   python -m pip install -r requirements-dev.txt
   ```

   `.env.test` is ignored by Git. Make sure it has test-only PostgreSQL credentials, a private `JWT_SECRET_KEY`, `API_BASE_URL=https://localhost:8443/api`, and `VERIFY_TLS=false`. The optional admin RBAC test is skipped unless `ADMIN_USERNAME` and `ADMIN_PASSWORD` are configured for an existing admin user.

2. Ensure the local NGINX certificate exists (see the Docker instructions), then start the isolated test stack and run pytest:

   ```sh
   docker compose --env-file .env.test -p bankapi-test up --build -d
   curl -k --fail https://localhost:8443/api/health
   pytest -v
   ```

3. Stop the test stack when finished:

   ```sh
   docker compose --env-file .env.test -p bankapi-test down
   ```

Use `docker compose --env-file .env.test -p bankapi-test logs` to inspect the test services. Add `-v` to the `down` command only when you also want to remove the isolated test database volume.