# Evidence

This document records implementation and verification evidence for the **FlyRank Capstone Social Media Studio** project.

---

## Project Overview

The project is a backend service for generating social-media content variants, reviewing and approving variants, scheduling approved content, and publishing it through pluggable publisher adapters.

### Main Technology Stack

- Python 3.12
- FastAPI
- SQLAlchemy 2.0
- PostgreSQL
- Alembic
- Redis
- Celery
- Celery Beat
- Mistral AI
- HTTPX
- Docker / Docker Compose

---

# Phase 1 — Foundation & Architecture

## Evidence

The initial project foundation was created with:

- FastAPI application structure
- Async SQLAlchemy setup
- PostgreSQL database configuration
- Docker Compose services
- Alembic migration support
- Project documentation

### Core Structure

```text
src/flyrank_capstone_social_studio/
├── api/
├── core/
├── models/
├── schemas/
└── services/
```

### Supporting Documentation

- `DESIGN.md`
- `README.md`
- `docker-compose.yml`
- `Dockerfile`
- Alembic configuration

---

# Phase 2 — Content Generation

## Evidence

Content generation functionality was implemented using Mistral AI.

The workflow supports:

```text
Create Post
    ↓
Generate Content
    ↓
Create Platform Variants
    ↓
Store Variants
```

### Database Models

- `Post`
- `Variant`

### Supported Platforms

- Telegram
- X
- LinkedIn

### Verification

Post and variant records were successfully persisted through PostgreSQL migrations and API workflows.

---

# Phase 3 — Variant Review & Approval

## Evidence

A review and approval workflow was implemented.

Variant states include:

```text
DRAFT
APPROVED
REJECTED
PUBLISHED
```

### Workflow

```text
Generated Variant
        ↓
       DRAFT
        ↓
   Review Action
     ↙       ↘
APPROVED   REJECTED
```

Only approved variants proceed to the scheduling and publishing workflow.

---

# Phase 4 — Publishing Adapters

## Evidence

The publishing system was designed using an adapter/factory architecture.

### Publisher Components

```text
publishers/
├── base.py
├── factory.py
├── mock_x.py
├── mock_linkedin.py
└── telegram.py
```

### Publishing Flow

```text
PublishingService
        ↓
PublisherFactory
        ↓
Platform Publisher
        ↓
External Platform API
```

### Implemented Publishers

- Mock X publisher
- Mock LinkedIn publisher
- Telegram publisher

The architecture allows publishers to be swapped without changing the main publishing service.

---

# Phase 5 — Scheduling & Background Publishing

## Evidence

Phase 5 implemented asynchronous scheduling, background publishing, publish history, idempotency, and recovery handling.

---

## 1. Celery Worker

The Celery worker successfully connected to Redis.

Example successful startup:

```text
Connected to redis://localhost:6380/0
celery@Latitude-3510 ready.
```

The registered tasks included:

```text
flyrank_capstone_social_studio.workers.tasks.check_due_schedule_slots
flyrank_capstone_social_studio.workers.tasks.publish_schedule_slot
flyrank_capstone_social_studio.workers.tasks.recover_stuck_schedule_slots
```

---

## 2. Celery Beat

Celery Beat successfully triggered scheduled background tasks.

Example evidence:

```text
Scheduler: Sending due task check-due-schedule-slots
```

The due-slot checker runs periodically to discover schedule slots that are ready for publishing.

The recovery task also runs periodically to handle slots that remain stuck in the processing state.

---

## 3. Due Schedule Detection

The system successfully detected due schedule slots.

Earlier verification logs showed:

```text
Due schedule slot found: <schedule-slot-id>
```

The final implementation evolved this workflow so that due slots are claimed for processing and dispatched to the publishing task.

---

## 4. Processing State

Schedule slots use processing state management to avoid duplicate dispatching.

The workflow is:

```text
PENDING
   ↓
PROCESSING
   ↓
 ┌───────────────┐
 ↓               ↓
SUCCESS        FAILED
```

A due schedule slot is claimed before the publishing task is dispatched.

This reduces the risk of multiple Celery Beat executions dispatching the same slot repeatedly.

---

## 5. Background Publishing

Publishing is performed asynchronously through Celery.

The workflow is:

```text
Celery Beat
    ↓
check_due_schedule_slots
    ↓
Schedule Slot Claimed
    ↓
PROCESSING
    ↓
publish_schedule_slot.delay(...)
    ↓
Celery Worker
    ↓
PublishingService
    ↓
PublisherFactory
    ↓
Platform Publisher
```

---

## 6. Idempotency Protection

Publishing uses an idempotency key based on the variant and schedule slot.

Conceptually:

```text
publish:<variant-id>:<schedule-slot-id>
```

Before creating a new publish attempt, the system checks whether an existing successful attempt already exists.

This protects against duplicate successful publishing when a task is retried or accidentally dispatched again.

---

## 7. Publish Attempt History

The `PublishAttempt` model records publishing activity.

Stored information includes:

- Schedule slot
- Idempotency key
- Platform
- Content
- Status
- External ID
- Error message
- Creation time
- Update time

### Publish Attempt States

```text
PENDING
SUCCESS
FAILED
```

This provides an auditable history of publishing activity.

---

## 8. Successful Telegram Publishing

The Telegram publisher was tested as part of the Phase 5 workflow.

The publishing request reached the Telegram API through:

```text
POST https://api.telegram.org/bot<TOKEN>/sendMessage
```

After correcting the test data and recreating the schedule flow, publishing was successfully verified.

The successful workflow was:

```text
Approved Variant
        ↓
Schedule Slot
        ↓
Due Slot Detection
        ↓
PROCESSING
        ↓
Telegram Publisher
        ↓
Publish Attempt
        ↓
SUCCESS
```

---

## 9. Failed Publishing Handling

A failed Telegram request was captured by the worker.

Evidence included an HTTP error:

```text
HTTP 400 Bad Request
```

The publishing service handles failures by:

1. Updating the `PublishAttempt` status to `FAILED`.
2. Saving the error message.
3. Allowing the failure to be visible in publish history.
4. Propagating the task failure to Celery logs.

This demonstrates that publishing failures are persisted instead of being silently ignored.

---

## 10. Recovery of Stuck Schedule Slots

A periodic recovery task was implemented:

```text
recover_stuck_schedule_slots
```

The task checks for schedule slots that remain in `PROCESSING` beyond the configured recovery timeout.

Verification logs showed recovery activity such as:

```text
Recovered unstarted schedule slot: <schedule-slot-id>
Recovered successful schedule slot: <schedule-slot-id>
```

The recovery workflow ensures that interrupted workers do not permanently leave schedule slots stuck in processing.

---

## 11. Database Migrations

Phase 5 schema changes were managed through Alembic.

Verification confirmed the database was upgraded to the latest migration:

```text
7a7c021bf3b5 (head)
```

Earlier Phase 5 migrations included schedule status and processing/recovery-related schema changes.

---

## 12. Final Phase 5 Workflow

The complete verified architecture is:

```text
Post
 ↓
Variant Generation
 ↓
Review
 ↓
APPROVED Variant
 ↓
Schedule Slot
 ↓
Celery Beat
 ↓
Check Due Slots
 ↓
Claim Slot
 ↓
PROCESSING
 ↓
Celery Worker
 ↓
Publishing Service
 ↓
Publisher Factory
 ↓
Platform Publisher
 ↓
Publish Attempt
 ↓
SUCCESS / FAILED
```

---

# Current Project Components

## API

```text
api/v1/
├── posts.py
└── publishing.py
```

## Models

```text
models/
├── post.py
├── variant.py
├── schedule_slot.py
└── publish_attempt.py
```

## Services

```text
services/
├── generation_service.py
├── constraint_service.py
├── variant_service.py
├── schedule_service.py
├── publishing_service.py
└── post_service.py
```

## Publishers

```text
publishers/
├── base.py
├── factory.py
├── mock_x.py
├── mock_linkedin.py
└── telegram.py
```

## Background Workers

```text
workers/
└── tasks.py
```

---

# Conclusion

The project currently provides a complete backend workflow for:

- Creating posts
- Generating platform-specific content variants
- Reviewing variants
- Approving or rejecting variants
- Scheduling approved variants
- Detecting due schedule slots
- Publishing asynchronously through Celery
- Supporting multiple publisher adapters
- Recording publish attempts
- Preventing duplicate successful publishing through idempotency
- Handling publishing failures
- Recovering stuck processing schedule slots
- Maintaining database migrations through Alembic

Phase 5 scheduling and background publishing functionality has been implemented and verified through Celery Worker, Celery Beat, database migrations, publishing workflows, failure handling, and recovery logs.
