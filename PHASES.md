# Project Phases

# FlyRank Capstone — Social Media Studio

This document defines the implementation phases for the Social Media Studio project and tracks the current completion status.

---

## Phase 1 — Foundation & Architecture

**Status: Completed**

### Goals

- Set up the FastAPI project.
- Define the application architecture.
- Configure PostgreSQL.
- Configure async SQLAlchemy.
- Configure Alembic migrations.
- Configure Docker and Docker Compose.
- Create the initial project documentation.

### Main Deliverables

- FastAPI application structure
- Async database configuration
- PostgreSQL service
- Redis service
- Alembic configuration
- Dockerfile
- Docker Compose configuration
- `DESIGN.md`
- Initial `README.md`

---

## Phase 2 — Content Generation

**Status: Completed**

### Goals

Build the content creation and AI generation workflow.

### Main Features

- Create posts.
- Generate social media content using Mistral AI.
- Create platform-specific variants.
- Persist posts and variants in PostgreSQL.
- Add validation and content constraints.

### Main Components

```text
models/
├── post.py
└── variant.py

services/
├── generation_service.py
├── constraint_service.py
├── post_service.py
└── variant_service.py
```

### Workflow

```text
Create Post
    ↓
Generate Content
    ↓
Validate Constraints
    ↓
Create Platform Variants
    ↓
Store in Database
```

---

## Phase 3 — Variant Review & Approval

**Status: Completed**

### Goals

Add a review workflow for generated variants.

### Main Features

- List generated variants.
- Review variants.
- Approve variants.
- Reject variants.
- Prevent invalid workflow transitions.

### Variant States

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
    Review
     ↙   ↘
APPROVED REJECTED
```

Only approved variants can continue to scheduling and publishing.

---

## Phase 4 — Publishing Adapters

**Status: Completed**

### Goals

Create an extensible publishing architecture.

### Main Features

- Publisher abstraction.
- Publisher factory.
- Mock X publisher.
- Mock LinkedIn publisher.
- Telegram publisher.
- Publishing service.

### Architecture

```text
PublishingService
        ↓
PublisherFactory
        ↓
SocialPublisher
        ↓
┌────────────┬───────────────┬──────────┐
│ Mock X     │ Mock LinkedIn │ Telegram │
└────────────┴───────────────┴──────────┘
```

### Main Components

```text
publishers/
├── base.py
├── factory.py
├── mock_x.py
├── mock_linkedin.py
└── telegram.py
```

The publisher architecture allows new social media platforms to be added without changing the core publishing workflow.

---

## Phase 5 — Scheduling & Background Publishing

**Status: Completed**

### Goals

Add asynchronous scheduling and reliable background publishing.

### Main Features

- Schedule approved variants.
- Store schedule slots in PostgreSQL.
- Detect due schedule slots.
- Process publishing through Celery workers.
- Run periodic checks through Celery Beat.
- Track publishing attempts.
- Prevent duplicate successful publishing.
- Handle publishing failures.
- Recover stuck processing schedule slots.
- Provide publish history.

### Main Components

```text
models/
├── schedule_slot.py
└── publish_attempt.py

services/
├── schedule_service.py
└── publishing_service.py

workers/
└── tasks.py

core/
└── celery.py
```

### Final Workflow

```text
Post
 ↓
Content Generation
 ↓
Platform Variants
 ↓
Review
 ↓
APPROVED
 ↓
Schedule Slot
 ↓
Celery Beat
 ↓
Check Due Schedule Slots
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

### Reliability Features

#### Idempotency

Each publishing operation uses an idempotency key based on the variant and schedule slot:

```text
publish:<variant-id>:<schedule-slot-id>
```

A previously successful publish attempt is returned instead of publishing the same content again.

#### Failure Tracking

Failed publishing attempts are stored with:

- Failed status
- Error message
- Platform
- Content
- Schedule slot reference

#### Recovery

A periodic Celery task checks for schedule slots that remain in `PROCESSING` beyond the configured timeout and recovers them.

---

# Current Project Status

| Phase | Description | Status |
|---|---|---|
| Phase 1 | Foundation & Architecture | Completed |
| Phase 2 | Content Generation | Completed |
| Phase 3 | Variant Review & Approval | Completed |
| Phase 4 | Publishing Adapters | Completed |
| Phase 5 | Scheduling & Background Publishing | Completed |

---

# Complete System Architecture

```text
                    ┌───────────────┐
                    │     Client    │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │    FastAPI    │
                    └───────┬───────┘
                            │
          ┌─────────────────┼─────────────────┐
          ▼                 ▼                 ▼
   ┌─────────────┐   ┌─────────────┐   ┌──────────────┐
   │ Generation  │   │   Review    │   │  Scheduling  │
   │   Service   │   │   Workflow  │   │   Service    │
   └──────┬──────┘   └─────────────┘   └──────┬───────┘
          │                                    │
          ▼                                    ▼
   ┌─────────────┐                     ┌─────────────┐
   │ PostgreSQL  │◄────────────────────│ ScheduleSlot│
   └─────────────┘                     └──────┬──────┘
                                               │
                                               ▼
                                        ┌─────────────┐
                                        │ Celery Beat │
                                        └──────┬──────┘
                                               │
                                               ▼
                                        ┌─────────────┐
                                        │    Redis    │
                                        └──────┬──────┘
                                               │
                                               ▼
                                        ┌─────────────┐
                                        │ Celery Worker│
                                        └──────┬──────┘
                                               │
                                               ▼
                                        ┌─────────────┐
                                        │ Publishing  │
                                        │   Service   │
                                        └──────┬──────┘
                                               │
                                               ▼
                                        ┌─────────────┐
                                        │  Publisher  │
                                        │   Factory   │
                                        └──────┬──────┘
                                               │
                              ┌────────────────┼────────────────┐
                              ▼                ▼                ▼
                         ┌─────────┐      ┌─────────┐     ┌─────────┐
                         │    X    │      │ LinkedIn│     │ Telegram│
                         └─────────┘      └─────────┘     └─────────┘
```

---

# Next Steps

The core backend workflow through Phase 5 is complete.

Future work can focus on areas such as:

- Automated tests
- API documentation improvements
- Authentication and user ownership
- Real X and LinkedIn integrations
- Retry policies and advanced task monitoring
- Production deployment
- Observability and structured logging
- Frontend application
