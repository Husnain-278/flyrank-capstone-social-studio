# Social Media Studio

A backend system for creating, validating, approving, scheduling, and
publishing social media content across multiple platforms.

This project was built as the FlyRank Capstone project using FastAPI,
PostgreSQL, Redis, Celery, Celery Beat, SQLAlchemy, and Mistral AI.

------------------------------------------------------------------------

## Features

-   Create social media posts
-   Generate platform-specific content variants using Mistral AI
-   Validate generated content against platform constraints
-   Approve or reject content variants
-   Schedule approved variants for publishing
-   Publish scheduled content in the background
-   Support multiple publishing platforms through a publisher adapter
    architecture
-   Track publishing attempts
-   Prevent duplicate publications using idempotency keys
-   Recover stuck schedule slots
-   Periodically detect and publish due schedule slots

# Architecture

The application follows a layered backend architecture.

``` text
                    ┌─────────────────┐
                    │     Client      │
                    │ Swagger/Postman │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │     FastAPI     │
                    │   API Layer     │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │    Services     │
                    │                 │
                    │ Post Service    │
                    │ Variant Service │
                    │ Schedule Service│
                    │ Publishing      │
                    └────────┬────────┘
                             │
                 ┌───────────┴───────────┐
                 ▼                       ▼
        ┌─────────────────┐      ┌─────────────────┐
        │   PostgreSQL    │      │      Redis      │
        │ Posts           │      │ Celery Broker   │
        │ Variants        │      └────────┬────────┘
        │ Schedule Slots  │               │
        │ Publish Attempts│               ▼
        └─────────────────┘      ┌─────────────────┐
                                 │     Celery      │
                                 │     Worker      │
                                 └────────┬────────┘
                                          │
                                          ▼
                                 ┌─────────────────┐
                                 │   Publishers    │
                                 │                 │
                                 │ Telegram        │
                                 │ Mock X          │
                                 │ Mock LinkedIn   │
                                 └─────────────────┘
```

# Scheduling and Publishing Flow

``` text
Approved Variant
        │
        ▼
Create Schedule Slot
        │
        ▼
PostgreSQL
        │
        ▼
Celery Beat
        │
        ▼
Check Due Schedule Slots
        │
        ▼
Claim Slot as PROCESSING
        │
        ▼
Celery Worker
        │
        ▼
Publishing Service
        │
        ▼
Publisher Factory
        │
        ├──────────────► Telegram Publisher
        │
        ├──────────────► Mock X Publisher
        │
        └──────────────► Mock LinkedIn Publisher
        │
        ▼
Create / Update Publish Attempt
        │
        ▼
SUCCESS or FAILED
```

# Tech Stack

## Backend

-   Python 3.12+
-   FastAPI
-   SQLAlchemy 2.0
-   Alembic
-   PostgreSQL

## Background Processing

-   Celery
-   Celery Beat
-   Redis

## AI

-   Mistral AI
-   LangChain Mistral AI

## HTTP Client

-   HTTPX

## Package Management

-   uv

## Infrastructure

-   Docker
-   Docker Compose

# Project Structure

``` text
.
├── alembic/
│   └── versions/
│
├── src/
│   └── flyrank_capstone_social_studio/
│       │
│       ├── api/
│       │   └── v1/
│       │       ├── posts.py
│       │       └── publishing.py
│       │
│       ├── core/
│       │   ├── celery.py
│       │   ├── config.py
│       │   ├── database.py
│       │   └── platforms.py
│       │
│       ├── models/
│       │   ├── post.py
│       │   ├── variant.py
│       │   ├── schedule_slot.py
│       │   └── publish_attempt.py
│       │
│       ├── publishers/
│       │   ├── base.py
│       │   ├── factory.py
│       │   ├── telegram.py
│       │   ├── mock_x.py
│       │   └── mock_linkedin.py
│       │
│       ├── schemas/
│       │
│       ├── services/
│       │   ├── generation_service.py
│       │   ├── constraint_service.py
│       │   ├── post_service.py
│       │   ├── variant_service.py
│       │   ├── schedule_service.py
│       │   └── publishing_service.py
│       │
│       ├── workers/
│       │   └── tasks.py
│       │
│       └── main.py
│
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
└── README.md
```

# Setup

## 1. Clone the Repository

``` bash
git clone <your-repository-url>
cd flyrank-capstone-social-studio
```

## 2. Install Dependencies

This project uses `uv`.

``` bash
uv sync
```

# Environment Variables

Create a `.env` file in the project root.

``` env
POSTGRES_DB=social_studio
POSTGRES_USER=social_studio_user
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

DATABASE_URL=postgresql+asyncpg://social_studio_user:your_password@localhost:5432/social_studio

REDIS_HOST=localhost
REDIS_PORT=6380

CELERY_BROKER_URL=redis://localhost:6380/0

TIMEZONE=Asia/Karachi

MISTRAL_API_KEY=your_mistral_api_key

TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
```

Never commit your real `.env` file or API keys.

# Start Infrastructure

Start PostgreSQL and Redis:

``` bash
docker compose up -d
```

Check containers:

``` bash
docker compose ps
```

# Database Migrations

Apply all migrations:

``` bash
uv run alembic upgrade head
```

Check the current migration:

``` bash
uv run alembic current
```

# Run the FastAPI Application

``` bash
uv run uvicorn flyrank_capstone_social_studio.main:app --reload
```

The API is available at `http://127.0.0.1:8000`.

Swagger documentation is available at `http://127.0.0.1:8000/docs`.

# Run Celery Worker

``` bash
uv run celery -A flyrank_capstone_social_studio.core.celery.celery_app worker --loglevel=info
```

The worker processes background publishing tasks.

# Run Celery Beat

``` bash
uv run celery -A flyrank_capstone_social_studio.core.celery.celery_app beat --loglevel=info
```

Celery Beat periodically performs:

-   Due schedule slot detection
-   Stuck schedule slot recovery

# Content Workflow

## 1. Create a Post

A post represents the original content that will be adapted for multiple
platforms.

``` text
Post
  ↓
Generate Variants
```

## 2. Generate Variants

The application generates platform-specific variants using Mistral AI.

Supported platforms:

-   Telegram
-   X
-   LinkedIn

``` text
Post
  ↓
Mistral AI
  ↓
Platform-specific Variants
```

## 3. Validate Variants

Generated variants are checked against platform-specific constraints.

Invalid variants cannot proceed through the publishing workflow.

## 4. Approve a Variant

A variant must be approved before it can be scheduled.

``` text
DRAFT
  ↓
APPROVED
```

Rejected or unapproved variants cannot be scheduled.

# Scheduling

Approved variants can be scheduled for future publishing.

``` text
APPROVED Variant
        ↓
Schedule Slot
        ↓
PENDING
```

The schedule slot is stored in PostgreSQL. Celery Beat periodically
checks for due schedule slots.

# Publishing

When a schedule slot becomes due:

``` text
PENDING
   ↓
PROCESSING
   ↓
Celery Publishing Task
   ↓
SUCCESS / FAILED
```

A successful publication updates:

``` text
ScheduleSlot → PUBLISHED
Variant → PUBLISHED
PublishAttempt → SUCCESS
```

# Idempotency

Each publication uses an idempotency key:

``` text
publish:{variant_id}:{schedule_slot_id}
```

If the same publishing task is processed again after a successful
publication, the existing successful `PublishAttempt` is returned
instead of publishing duplicate content.

This protects against:

-   Celery retries
-   Worker restarts
-   Duplicate task execution

# Stuck Schedule Slot Recovery

A schedule slot can become stuck in the `PROCESSING` state if a worker
crashes during execution.

Celery Beat periodically runs a recovery task that checks stuck schedule
slots and restores them to the appropriate state.

This allows publishing to continue after worker failures while avoiding
duplicate successful publications.

# Publisher Architecture

``` text
PublishingService
        ↓
PublisherFactory
        ↓
SocialPublisher
        ↓
─────────────────────────────────
│              │                │
Telegram      X            LinkedIn
Publisher     Mock          Mock
```

Each platform publisher implements the same publishing interface. This
allows platform implementations to be swapped or replaced without
changing the publishing service.

# Supported Publishers

## Telegram

Uses the real Telegram Bot API.

Required environment variables:

``` env
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
```

## X

Currently implemented as a mock publisher.

## LinkedIn

Currently implemented as a mock publisher.

# Publish Attempts

Every publishing attempt is stored in the database.

A `PublishAttempt` records:

-   Schedule slot
-   Platform
-   Content
-   Status
-   Idempotency key
-   External platform ID
-   Error message
-   Creation time
-   Update time

Possible statuses:

``` text
PENDING
SUCCESS
FAILED
```

# API Documentation

Interactive API documentation is available through FastAPI Swagger at
`http://127.0.0.1:8000/docs`.

The API includes functionality for:

-   Posts
-   Variants
-   Variant approval/rejection
-   Scheduling
-   Publishing
-   Publish attempt history

# Testing the Complete Workflow

Start all required services.

## Terminal 1 --- FastAPI

``` bash
uv run uvicorn flyrank_capstone_social_studio.main:app --reload
```

## Terminal 2 --- Celery Worker

``` bash
uv run celery -A flyrank_capstone_social_studio.core.celery.celery_app worker --loglevel=info
```

## Terminal 3 --- Celery Beat

``` bash
uv run celery -A flyrank_capstone_social_studio.core.celery.celery_app beat --loglevel=info
```

Then perform the workflow:

``` text
1. Create Post
        ↓
2. Generate Variant
        ↓
3. Approve Variant
        ↓
4. Create Schedule Slot
        ↓
5. Wait until scheduled_for time
        ↓
6. Celery Beat detects due slot
        ↓
7. Worker publishes content
        ↓
8. PublishAttempt becomes SUCCESS
        ↓
9. ScheduleSlot becomes PUBLISHED
        ↓
10. Variant becomes PUBLISHED
```

# Development

## Run Tests

``` bash
uv run pytest
```

## Lint

``` bash
uv run ruff check .
```

# Known Limitations

-   Only Telegram currently uses a real publishing API.
-   X publishing is currently mocked.
-   LinkedIn publishing is currently mocked.
-   The project currently focuses on backend functionality.
-   Authentication and multi-user account management are outside the
    current project scope.

# License

This project was created as part of the FlyRank Capstone project.
