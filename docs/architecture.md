# Architecture

The project follows a layered architecture. Each layer has a single responsibility. This separation improves maintainability, testing, and scalability.

## Application Flow

FastAPI
    │
    ▼
Routers (API Layer - Receives HTTP requests)
    │
    ▼
Services (Service Layer - Contains business logic)
    │
    ▼
Repositories (Repository Layer - Handles database access)
    │
    ▼
SQLAlchemy (ORM)
    │
    ▼
PostgreSQL (Database - Stores persistent data)

## Middleware
Middleware intercepts requests and responses to handle cross-cutting concerns:
- Logging
- CORS (Cross-Origin Resource Sharing)
- Request IDs
- Timing

## Dependency Injection
FastAPI's dependency injection system is used for:
- Authentication (Extracting tokens)
- Database Session (Yielding DB connections)
- Current User (Providing the authenticated user to routes)

## Database Architecture

**users**
- id
- email
- hashed_password
- created_at

**conversations**
- id
- user_id
- title
- created_at
- updated_at
- deleted_at

**Relationships**
One User
   ↓
Many Conversations

## Tech Stack & Tooling

- **Authentication:** JWT (JSON Web Tokens)
- **Password Hashing:** pwdlib
- **ORM:** SQLAlchemy
- **Validation:** Pydantic
- **Migrations:** Alembic
- **Configuration:** Environment variables
- **Logging:** Python logging