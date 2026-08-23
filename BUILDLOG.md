# BUILDLOG

## Project

**FlyRank Capstone – Social Media Studio**

This document summarizes the development process, major implementation decisions, use of AI assistance, and the adjustments made while building the project.

---

## Development Approach

The project was developed incrementally across five phases:

1. Project design and architecture
2. Post ingestion and AI-powered variant generation
3. Review and approval workflow
4. Publisher adapters and publishing
5. Durable scheduling, Celery workers, recovery, and hardening

Each phase was implemented, run locally, and manually verified before moving to the next phase.

---

## AI Assistance

AI assistance was used as a development companion throughout the project. It helped with:

- Breaking the capstone specification into manageable implementation phases
- Discussing the project architecture and data model
- Exploring SQLAlchemy async patterns and relationships
- Reviewing FastAPI, Celery, and scheduling flows
- Generating implementation suggestions and code drafts
- Troubleshooting errors from migrations, PostgreSQL, Celery, Redis, and HTTP publishing
- Reviewing edge cases around idempotency, duplicate publishing, and stuck schedule recovery
- Improving project documentation

AI was used to accelerate development and learning, but the implementation was developed iteratively in the local environment. Code was integrated, adjusted, executed, and debugged based on the actual behavior of the application.

---

## Where AI Suggestions Needed Adjustment

Some AI-generated suggestions required changes after being tested in the real project environment.

Examples included:

- Adjusting Celery task discovery and worker configuration
- Refining the schedule-slot claiming and recovery flow to avoid repeated processing
- Updating database queries based on actual SQLAlchemy behavior
- Correcting migration workflow after reviewing generated Alembic revisions
- Handling publishing failures returned by the Telegram API
- Improving recovery logic so previously successful or unstarted schedule slots were handled correctly
- Adjusting environment and Docker commands based on the local setup

These cases were resolved by inspecting logs, checking application state, testing the workflow, and updating the implementation.

---

## Key Technical Decisions

### FastAPI and SQLAlchemy

FastAPI was used for the API layer with asynchronous SQLAlchemy sessions and PostgreSQL for persistent storage.

### AI Variant Generation

Mistral AI was integrated for generating platform-specific content variants. Generated content is stored as variants and passes through validation and review before publishing.

### Review Workflow

Variants follow a controlled lifecycle:

```text
Draft → Approved → Scheduled → Published
             ↓
          Rejected
```

Only approved variants can be scheduled.

### Publisher Adapter Architecture

Publishing is separated behind a common publisher interface.

The project currently supports:

- Telegram publisher
- Mock X publisher
- Mock LinkedIn publisher

This makes it possible to add or replace platform integrations without changing the core publishing workflow.

### Durable Scheduling

Scheduling state is stored in PostgreSQL rather than relying only on in-memory task scheduling.

Celery Beat periodically checks for due schedule slots, while Celery workers process publishing tasks.

### Idempotency

Each publishing operation uses a deterministic idempotency key. Successful publish attempts are recorded so the same schedule slot is not published again unnecessarily.

### Recovery

Schedule slots use processing state and timeout-based recovery logic to handle cases where a worker may stop after claiming a job.

---

## Verification

The main application workflows were manually verified during development, including:

- Creating and storing posts
- Generating variants
- Validating platform constraints
- Approving and rejecting variants
- Blocking invalid scheduling attempts
- Creating schedule slots
- Detecting due schedule slots with Celery Beat
- Processing publishing tasks with Celery workers
- Recording successful and failed publish attempts
- Preventing duplicate successful publishing
- Recovering schedule slots left in processing state

Evidence from these workflows is documented separately in `EVIDENCE.md`.

Automated tests were not implemented as part of this development iteration. The project workflows were instead exercised manually during implementation and debugging.

---

## What I Learned

This project provided practical experience with:

- Async FastAPI applications
- SQLAlchemy async ORM patterns
- Alembic migrations
- PostgreSQL relationships and persistent state
- Celery workers and Celery Beat
- Redis as a message broker
- Durable scheduling patterns
- Background task recovery
- Idempotency in external publishing workflows
- Adapter and factory patterns
- Integrating an LLM into a backend application
- Debugging distributed and asynchronous workflows

---

## Final Notes

The project was built iteratively from the capstone requirements and evolved through implementation, debugging, and manual verification.

AI assistance was used to speed up exploration and development, while the final implementation was shaped through hands-on testing, debugging, architectural decisions, and adjustments based on the actual behavior of the application.
