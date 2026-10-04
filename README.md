# Banking Transaction API

[![Banking API CI](https://github.com/kaustuvnn1-maker/banking-transaction-api/actions/workflows/ci.yml/badge.svg)](https://github.com/kaustuvnn1-maker/banking-transaction-api/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.13-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-API-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)
![Docker](https://img.shields.io/badge/Docker-Compose-blue)
![NGINX](https://img.shields.io/badge/NGINX-Gateway-green)

A **production-style banking transaction API** built with FastAPI, PostgreSQL, SQLAlchemy, Alembic, NGINX, Docker Compose, JWT authentication, RBAC, ownership authorization, idempotency, concurrency controls, TLS, structured logging, automated regression tests, and GitHub Actions CI.

This project goes beyond CRUD. Its main focus is **financial correctness under failures, retries, concurrent requests, and unauthorized access**.

> **Project status:** Complete for portfolio / learning scope.  
> This is a production-oriented engineering project, not a real regulated banking platform.

---

## Why this project exists

A banking API has to solve much harder problems than simply creating and reading records.

This project was designed around questions such as:

- What happens if a debit succeeds but the credit fails?
- What happens if two requests try to spend the same balance at the same time?
- What happens if a client retries a transfer after losing the first response?
- How do we stop a valid user from reading another customer's account?
- How do we prevent a public user from assigning themselves the `ADMIN` role?
- How do we trace one request through the gateway, application, and logs?
- How do we safely evolve a database schema?
- How do we prove the application works on a clean machine, not only on a developer laptop?

The result is a layered API that combines **application security, transactional integrity, concurrency control, gateway protections, observability, testing, and CI**.

---

## Key engineering capabilities

| Area | Implementation |
|---|---|
| API framework | FastAPI with modular routers and service layer |
| Validation | Pydantic request / response schemas |
| Database | PostgreSQL 16 + SQLAlchemy ORM |
| Schema evolution | Alembic migrations |
| Money handling | `Decimal` + PostgreSQL `NUMERIC(12,2)` |
| Atomicity | Debit + credit + transaction log committed together |
| Concurrency | PostgreSQL `SELECT ... FOR UPDATE` row locking |
| Deadlock reduction | Deterministic account lock ordering |
| Retry safety | `Idempotency-Key` + DB uniqueness constraint |
| Authentication | JWT bearer tokens with expiry and signature validation |
| Password security | Password hashing via `pwdlib` |
| Authorization | Ownership checks + CUSTOMER / ADMIN RBAC |
| Privilege protection | Public registration cannot self-assign admin role |
| Gateway | NGINX reverse proxy |
| Gateway controls | TLS, rate limiting, CORS, security headers, header forwarding |
| Observability | Correlation IDs, request timing, JSON structured logging |
| Runtime | Docker Compose: NGINX + FastAPI + PostgreSQL |
| Persistence | Docker named volume for PostgreSQL data |
| Testing | 40+ integration / regression test cases |
| CI | GitHub Actions rebuilds the stack and runs pytest on push / PR |
| Merge safety | Protected `main` with required CI status checks |

---

## System architecture

```mermaid
flowchart LR
    Client["Client / Postman / Browser"] -->|"HTTPS :8443<br/>TLS 1.2 / 1.3"| NGINX

    subgraph Docker["Docker Compose Network"]
        NGINX["NGINX API Gateway<br/><br/>Reverse Proxy<br/>TLS Termination<br/>Rate Limiting<br/>CORS<br/>Security Headers"]
        API["FastAPI Application<br/><br/>JWT Authentication<br/>RBAC<br/>Ownership Checks<br/>Idempotency<br/>Business Logic<br/>Structured Logging"]
        DB["PostgreSQL 16<br/><br/>Transactions<br/>Row Locks<br/>Constraints<br/>Audit Records"]
    end

    NGINX -->|"HTTP<br/>api:8000"| API
    API -->|"SQLAlchemy / psycopg2<br/>db:5432"| DB
    DB --> Volume[("postgres_data<br/>Docker Volume")]

    CI["GitHub Actions CI"] -.->|"Build + Test"| Docker
```

### Responsibility boundaries

```text
NGINX
  -> transport and edge controls

FastAPI
  -> identity, authorization, validation and business logic

PostgreSQL
  -> transaction integrity, locking, constraints and persistence
```

This separation keeps gateway concerns out of business logic and keeps data-integrity guarantees inside the database transaction boundary.

---

## User journey

```mermaid
flowchart TD
    A["New Customer"] --> B["POST /auth/register"]
    B --> C["Customer created<br/>role = customer"]
    C --> D["POST /auth/login"]
    D --> E["Receive JWT access token"]
    E --> F["POST /accounts"]
    F --> G["Create owned bank account"]
    G --> H["GET /accounts"]
    H --> I["View own accounts"]
    I --> J["POST /transfers<br/>JWT + Idempotency-Key"]
    J --> K["Transfer processed safely"]
    K --> L["GET /accounts/{id}/transactions"]
    L --> M["View account transaction history"]

    N["Existing ADMIN"] --> O["POST /admin/register"]
    O --> P["Create another admin"]
    N --> Q["GET /transactions"]
    Q --> R["Audit all transactions"]
```

---

## Secure transfer sequence

This is the most important flow in the project.

```mermaid
sequenceDiagram
    autonumber

    participant C as Client
    participant N as NGINX
    participant A as FastAPI Router
    participant Auth as JWT/Auth Dependency
    participant S as Transfer Service
    participant DB as PostgreSQL

    C->>N: POST /api/transfers<br/>JWT + Idempotency-Key
    N->>N: TLS termination<br/>rate limit<br/>CORS/security headers
    N->>A: Forward request

    A->>Auth: Validate bearer token
    Auth->>DB: Load user from token subject
    DB-->>Auth: User
    Auth-->>A: Authenticated user

    A->>S: transfer_money(...)
    S->>DB: Lookup Idempotency-Key

    alt Same key + same request
        DB-->>S: Existing transaction
        S-->>A: Already processed
        A-->>N: 200 OK
        N-->>C: Safe retry response
    else Same key + different request
        S-->>A: IDEM_KEY_REUSED
        A-->>N: 409 Conflict
        N-->>C: 409 Conflict
    else New logical transfer
        S->>DB: Lock rows in deterministic ID order<br/>SELECT ... FOR UPDATE
        DB-->>S: Locked source + destination

        S->>S: Verify source ownership
        S->>S: Verify sufficient balance

        alt Ownership failure
            S-->>A: 403 Forbidden
            A-->>C: Forbidden
        else Insufficient balance
            S-->>A: 400 Business Error
            A-->>C: Transfer rejected
        else Valid transfer
            S->>DB: Debit source
            S->>DB: Credit destination
            S->>DB: Insert transaction audit record
            S->>DB: COMMIT
            DB-->>S: Success
            S-->>A: Transfer successful
            A-->>N: 200 OK + Correlation ID
            N-->>C: HTTPS response
        end
    end
```

### Why multiple controls are required

| Mechanism | Problem solved |
|---|---|
| Database transaction | Prevents partial debit / credit |
| Row-level locking | Prevents concurrent balance races / double spending |
| Deterministic lock ordering | Reduces common deadlock scenarios |
| Idempotency key | Prevents duplicate financial effects on retry |
| Unique DB constraint | Closes simultaneous duplicate-key race conditions |
| JWT | Establishes caller identity |
| Ownership check | Prevents object-level authorization failures |
| RBAC | Restricts privileged operations |
| Correlation ID | Makes one request traceable across logs |

---

## Data model

```mermaid
erDiagram
    USER_LOGIN ||--o{ ACCOUNT : owns
    ACCOUNT ||--o{ TRANSACTION : source
    ACCOUNT ||--o{ TRANSACTION : destination

    USER_LOGIN {
        int userID PK
        string username UK
        string password_hash
        string role
    }

    ACCOUNT {
        int id PK
        string account_holder_name
        decimal balance
        int user_id FK
    }

    TRANSACTION {
        int id PK
        int account_id_from FK
        int account_id_to FK
        decimal amount
        datetime transaction_date
        string transaction_status
        string idem_key UK
    }
```

---

## API endpoints

All routes below are shown without the external NGINX `/api` prefix.

| Method | Endpoint | Access | Purpose |
|---|---|---|---|
| `GET` | `/health` | Public | Health check |
| `POST` | `/auth/register` | Public | Register a customer |
| `POST` | `/auth/login` | Public | Authenticate and issue JWT |
| `POST` | `/accounts` | Authenticated | Create an account owned by the current user |
| `GET` | `/accounts` | Authenticated | Customer: own accounts; Admin: all accounts |
| `GET` | `/accounts/{account_id}` | Authenticated + owner | View a specific owned account |
| `GET` | `/accounts/{account_id}/transactions` | Authenticated + owner | View transaction history for an owned account |
| `POST` | `/transfers` | Authenticated + source owner | Execute an idempotent transfer |
| `GET` | `/transactions` | ADMIN | View all transaction audit records |
| `POST` | `/admin/register` | ADMIN | Create another admin user |

### Transfer request

```http
POST /api/transfers
Authorization: Bearer <JWT>
Idempotency-Key: <unique-logical-request-id>
Content-Type: application/json
```

```json
{
  "from_account": 101,
  "to_account": 202,
  "amount": "250.00"
}
```

---

## Security model

### Authentication

Protected endpoints require:

```http
Authorization: Bearer <JWT>
```

The application validates:

- bearer scheme;
- JWT signature;
- explicit allowed algorithm (`HS256`);
- token expiry;
- `sub` user identity;
- existence of the user in PostgreSQL.

Expected behavior:

```text
Missing / invalid / expired token -> 401
Valid identity but forbidden action -> 403
```

### Password handling

Passwords are never stored as plaintext.

```text
plaintext password
    -> pwdlib PasswordHash.recommended()
    -> password hash stored in PostgreSQL
```

Login intentionally returns the same generic failure message for unknown usernames and wrong passwords.

### Object-level authorization

A valid JWT does not automatically authorize access to every account.

For customer-owned resources, the application checks:

```text
account.user_id == current_user.userID
```

This protects account details, transaction history, and transfer source accounts from cross-user access.

### RBAC

Current roles:

```text
CUSTOMER
ADMIN
```

Public registration cannot accept a caller-controlled role. The public schema forbids extra fields, and customer registration defaults to the `customer` role.

Admin creation requires an already-authenticated admin.

### Gateway security

NGINX provides:

- TLS 1.2 / 1.3;
- reverse proxying;
- IP-based rate limiting (`5r/s`, burst `10`);
- CORS allowlist;
- security headers;
- `Authorization` forwarding;
- `Idempotency-Key` forwarding;
- `X-Correlation-ID` forwarding;
- `X-Forwarded-*` metadata.

Current security headers include:

```text
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 0
Referrer-Policy: no-referrer
Content-Security-Policy: default-src 'none'; ...
```

### Secrets

Secrets and local certificate material are intentionally excluded from Git.

Examples:

```text
.env
.env.docker
.env.test
certs/
*.key
*.crt
```

`.env.example` contains test / placeholder values only.

> The project implements controls relevant to several OWASP API Security risks, but no formal OWASP compliance assessment is claimed.

---

## Transaction integrity and concurrency

### Atomic transfer

The transfer performs:

```text
debit source
+ credit destination
+ insert transaction record
+ COMMIT
```

as one database transaction.

If an unexpected error occurs:

```text
ROLLBACK
```

so partial financial effects do not survive.

### Row-level locking

Account rows are loaded using:

```sql
SELECT ... FOR UPDATE
```

before balance mutation.

Accounts are locked in sorted account-ID order to reduce circular lock acquisition.

### Idempotency

The caller provides:

```http
Idempotency-Key: <value>
```

Behavior:

```text
new key
-> execute transfer

same key + same request
-> return already processed result
-> no second financial effect

same key + different request
-> 409 Conflict
```

A unique database constraint on the idempotency key provides the final race-condition safeguard.

---

## Failure scenarios intentionally covered

| Scenario | Expected result |
|---|---|
| Missing JWT | `401` |
| Invalid / tampered JWT | `401` |
| Expired JWT | `401` |
| Customer accesses another customer's account | `403` |
| Customer accesses another customer's transaction history | `403` |
| Customer calls admin-only transaction audit | `403` |
| Public registration tries `role=ADMIN` | Rejected |
| Negative / zero transfer amount | `422` |
| Same source and destination | Business rejection |
| Insufficient balance | Transfer rejected, balances unchanged |
| Concurrent overspend attempts | Only one transfer succeeds |
| Retry with same idempotency key | Money moves once |
| Same key reused for different request | `409` |
| Disallowed CORS origin | Origin is not reflected |
| Excessive request rate | NGINX returns `429` |

---

## Observability

Every request receives a correlation ID.

If the client sends:

```http
X-Correlation-ID: my-request-id
```

the application preserves it.

Otherwise, a UUID is generated automatically.

Structured JSON logs capture:

```text
timestamp
level
logger
message
correlation_id
method
path
status_code
duration_ms
query_params
error / exception
```

Sensitive credentials and authorization tokens are not intentionally logged.

---

## Automated testing

The repository contains **40+ integration / regression test cases** covering:

```text
tests/
├── test_health.py
├── test_auth.py
├── test_accounts.py
├── test_transfers.py
├── test_rbac.py
├── test_gateway.py
├── test_concurrency.py
└── test_rate_limit.py
```

The tests exercise the real path:

```text
pytest
  -> HTTPS
  -> NGINX
  -> FastAPI
  -> SQLAlchemy
  -> PostgreSQL
```

Important regression coverage includes:

- registration and login;
- invalid, tampered and expired JWTs;
- ownership / IDOR-style checks;
- RBAC;
- request validation;
- idempotency;
- transaction rollback behavior;
- concurrent double-spend prevention;
- concurrent duplicate-idempotency handling;
- CORS;
- security headers;
- correlation IDs;
- rate limiting.

The rate-limit test is intentionally opt-in because it deliberately floods the gateway.

---

## CI / Pull Request workflow

```mermaid
flowchart LR
    Dev["Developer"] --> Branch["Feature Branch"]
    Branch --> PR["Pull Request -> main"]
    PR --> CI["GitHub Actions"]

    CI --> Checkout["Checkout repository"]
    Checkout --> Python["Set up Python"]
    Python --> Env["Create temporary test env"]
    Env --> TLS["Generate temporary TLS certificate"]
    TLS --> Compose["Validate + Build Docker Compose"]
    Compose --> Health["Wait for HTTPS health check"]
    Health --> Tests["Run pytest"]

    Tests -->|Fail| Block["Required check fails<br/>Merge blocked"]
    Tests -->|Pass| Green["Required check passes"]
    Green --> Merge["Merge into protected main"]
```

GitHub Actions performs the following on pushes and pull requests targeting `main`:

1. checks out the repository;
2. installs Python test dependencies;
3. creates temporary CI environment values;
4. generates a temporary self-signed TLS certificate;
5. validates Docker Compose;
6. builds and starts PostgreSQL, FastAPI, and NGINX;
7. applies Alembic migrations;
8. waits for the HTTPS health endpoint;
9. runs pytest;
10. prints Docker logs on failure;
11. always destroys the temporary CI stack.

The `main` branch uses required CI checks before merge.

---

## Repository structure

```text
banking-transaction-api/
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── alembic/
│   └── versions/
│
├── database/
│   ├── accounts.py
│   ├── connections.py
│   ├── transaction_log.py
│   └── user_login_details.py
│
├── dependencies/
│   └── auth.py
│
├── exceptions/
│   └── business_exception.py
│
├── middleware/
│   └── request_middleware.py
│
├── nginx/
│   └── docker.conf
│
├── routes/
│   ├── create_account_route.py
│   ├── create_admin_route.py
│   ├── get_accounts_route.py
│   ├── get_transactions_route.py
│   ├── login_user_route.py
│   ├── new_user_creation_route.py
│   └── transfer_route.py
│
├── schemas/
├── scripts/
├── service/
├── tests/
├── .dockerignore
├── .env.example
├── .gitignore
├── alembic.ini
├── compose.yaml
├── Dockerfile
├── main.py
├── pytest.ini
├── requirements-dev.txt
├── requirements.txt
└── README.md
```

### Layering rule

```text
Route
  -> HTTP contract, Depends, headers

Schema
  -> request / response validation

Dependency
  -> reusable authentication

Service
  -> business rules and transaction orchestration

Database / ORM
  -> persistence model

Middleware
  -> cross-cutting request logging / correlation

NGINX
  -> edge / gateway controls
```

---

## Quick start with Docker Compose

### Prerequisites

- Docker Desktop
- Docker Compose v2
- OpenSSL
- curl or Postman

### 1. Create local environment

```bash
cp .env.example .env
```

Replace the placeholder / test values with local development values.

Do not commit `.env`.

### 2. Generate local TLS certificate

```bash
mkdir -p certs

openssl req \
  -x509 \
  -nodes \
  -newkey rsa:2048 \
  -keyout certs/server.key \
  -out certs/server.crt \
  -days 365 \
  -subj "/CN=localhost" \
  -addext "subjectAltName=DNS:localhost,IP:127.0.0.1"
```

### 3. Build and start

```bash
docker compose up --build -d
```

Startup flow:

```text
PostgreSQL
   -> healthcheck passes
FastAPI
   -> alembic upgrade head
   -> Uvicorn starts
NGINX
   -> HTTPS gateway becomes available
```

### 4. Verify

```bash
curl -k https://localhost:8443/api/health
```

Expected:

```json
{"status":"ok"}
```

### 5. Inspect

```bash
docker compose ps
docker compose logs -f
```

### 6. Stop

```bash
docker compose down
```

This preserves the PostgreSQL named volume.

To remove the development database volume as well:

```bash
docker compose down -v
```

> `-v` deletes the database volume. Use it only when you intentionally want to destroy the stored database state.

---

## Run without Docker

Create a Python environment:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Configure local PostgreSQL and environment variables:

```bash
export DATABASE_URL="postgresql+psycopg2://USER:PASSWORD@localhost:5432/bankapidb"
export JWT_SECRET_KEY="replace-with-a-long-random-secret"
```

Apply migrations:

```bash
alembic upgrade head
```

Start FastAPI:

```bash
uvicorn main:app --reload
```

Health:

```text
http://127.0.0.1:8000/health
```

Swagger UI when running FastAPI directly:

```text
http://127.0.0.1:8000/docs
```

---

## Run the test suite

Create an isolated test environment:

```bash
cp .env.example .env.test
```

Install test dependencies:

```bash
python -m pip install -r requirements-dev.txt
```

Start an isolated Compose project:

```bash
docker compose \
  --env-file .env.test \
  -p bankapi-test \
  up --build -d
```

Verify:

```bash
curl -k --fail https://localhost:8443/api/health
```

Run tests:

```bash
pytest -v
```

Optional gateway rate-limit test:

```bash
RUN_RATE_LIMIT_TESTS=1 \
pytest tests/test_rate_limit.py -v
```

Clean the disposable test environment:

```bash
docker compose \
  --env-file .env.test \
  -p bankapi-test \
  down -v
```

---

## Database migrations

Schema changes are managed through Alembic rather than `Base.metadata.create_all()`.

### Create a migration

```bash
alembic revision --autogenerate -m "describe the change"
```

Always review the generated revision.

### Apply migrations

```bash
alembic upgrade head
```

### Inspect current revision

```bash
alembic current
```

### Development downgrade

```bash
alembic downgrade <revision>
```

Database migration flow:

```text
ORM model change
    -> Alembic revision
    -> migration review
    -> upgrade
    -> PostgreSQL schema updated
```

---

## How to add a new endpoint

Future changes should preserve the architecture rather than putting everything into `main.py`.

### 1. Define the contract

Before coding, specify:

```text
HTTP method
URL
request body
response body
authentication requirement
ownership requirement
role requirement
business failures
database changes
idempotency requirement
```

### 2. Create / update the Pydantic schema

Put structural request and response validation under `schemas/`.

Examples:

```text
positive numbers
non-empty strings
field length
allowed enum values
forbidden client-controlled fields
```

### 3. Decide authorization before business logic

Ask:

```text
Public?
Authenticated?
Owner-only?
ADMIN-only?
Owner OR ADMIN?
```

Reuse the existing authentication dependency instead of decoding JWT inside each route.

### 4. Implement service-layer logic

Business rules belong under `service/`.

The service layer should handle:

- resource lookup;
- ownership / role decisions;
- business validation;
- transaction boundaries;
- commit / rollback;
- domain errors.

### 5. Add database changes only when required

If a new table / field / index / constraint is needed:

```text
update ORM model
    -> create Alembic revision
    -> review migration
    -> upgrade test DB
```

### 6. Add the route

Routes should remain thin:

```text
request
 -> schema
 -> dependencies
 -> service
 -> response
```

### 7. Add regression tests

At minimum test:

```text
happy path
validation failure
missing authentication
forbidden authorization
resource not found
business failure
database effect
```

For money-moving or retry-sensitive operations also test:

```text
idempotency
concurrency
rollback
```

### 8. Use the normal Git workflow

```text
feature branch
  -> commit
  -> push
  -> pull request
  -> required GitHub Actions CI
  -> merge only when green
```

---

## Engineering decisions and trade-offs

| Decision | Reason |
|---|---|
| PostgreSQL instead of SQLite | Real row locking, concurrency and production-style relational behavior |
| `Decimal` / `NUMERIC` for money | Avoid floating-point money errors |
| Alembic instead of `create_all()` | Explicit, repeatable schema evolution |
| JWT dependency | Centralized authentication logic |
| Ownership checks in services | Prevent authenticated cross-customer access |
| NGINX at the edge | Separate gateway controls from business logic |
| TLS terminated at NGINX | External traffic encrypted while keeping simple private container networking |
| Docker Compose | Reproducible multi-service environment |
| Test through NGINX | Validate the real gateway-to-API path |
| Required CI checks | Prevent untested changes from reaching `main` |
| Deterministic lock order | Reduce transfer deadlock risk |
| DB uniqueness for idempotency | Protect against simultaneous duplicate requests |

---

## Known limitations

This repository intentionally stops at a strong production-style portfolio scope.

It does **not** claim to be a regulated production banking system.

Current limitations include:

- self-signed certificates are used for local development;
- no managed cloud secret store;
- no production CA certificate automation;
- no token refresh / token revocation service;
- NGINX rate limiting is local to the gateway instance rather than distributed;
- no double-entry accounting ledger;
- no external KYC / AML / payment-network integrations;
- no formal OWASP API Top 10 compliance assessment;
- no real cloud UAT / production deployment;
- no formal regulatory / PCI / banking compliance certification.

These would be separate engineering and governance workstreams in a real financial institution.

---

## What this project demonstrates

This project is intended to demonstrate the ability to reason about an API as a **system**, not only as a collection of endpoints.

The main engineering themes are:

```text
Correctness under failure
Concurrency safety
Retry safety
Authentication
Authorization
Privilege boundaries
Database migrations
Gateway security
Transport security
Observability
Containerization
Automated regression testing
Continuous Integration
Protected Pull Request workflow
```

The core transfer design can be summarized as:

```text
Atomicity
  + Row Locking
  + Idempotency
  + Ownership Authorization
  + Database Constraints
  = Safer Financial Transaction Processing
```

---

## Project lifecycle completed

```text
Design
  -> API development
  -> PostgreSQL persistence
  -> Alembic migrations
  -> atomic transaction handling
  -> concurrency testing
  -> idempotency
  -> JWT authentication
  -> ownership authorization
  -> RBAC
  -> structured logging
  -> NGINX gateway
  -> TLS
  -> Docker Compose
  -> automated regression tests
  -> GitHub Actions CI
  -> protected main branch
  -> feature branch / Pull Request workflow
  -> CI failure + recovery validation
  -> documentation
```

**Status: Complete for portfolio scope.**
