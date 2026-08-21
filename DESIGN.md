# Social Media Studio — Design

## 1. Problem

Social Media Studio transforms a single blog post into platform-specific social media variants.

A user provides a blog post as either a URL or pasted Markdown. The system stores the post as the single source of truth and generates a variant for each configured social media platform.

Each variant must satisfy its platform's constraint profile before entering the review workflow. A user can approve, edit, or reject a variant.

Only approved variants can be scheduled for publishing.

Scheduled publishing must be reliable and idempotent. Retrying a publishing operation or restarting a worker must never cause the same variant to be published twice for the same scheduled slot.

The application communicates with publishing platforms through a common `SocialPublisher` interface. This allows a publishing adapter to be changed without modifying business logic.

The system will use Telegram as the real publishing target and mock adapters for X and LinkedIn.

---

## 2. Core Architecture

```text
Client
   │
   ▼
FastAPI
   │
   ├── Post Ingestion
   │
   ├── Variant Generation
   │       │
   │       ▼
   │   LangChain
   │       │
   │       ▼
   │   Mistral AI
   │
   ├── Constraint Validation
   │
   ├── Review Workflow
   │
   └── Scheduling
           │
           ▼
       PostgreSQL
           │
           ▼
        Celery
           │
           ▼
         Redis
           │
           ▼
     Celery Worker
           │
           ▼
    SocialPublisher
     ├── TelegramPublisher
     ├── MockXPublisher
     └── MockLinkedInPublisher
```

### Core Responsibilities

- **FastAPI** handles the REST API and application entry points.
- **PostgreSQL** stores posts, variants, schedules, and publish history.
- **LangChain + Mistral AI** generate platform-specific variants.
- **Constraint Validation** enforces platform rules independently of the LLM.
- **Celery + Redis** handle background publishing tasks.
- **Celery Beat** identifies and triggers due scheduled publishing work.
- **SocialPublisher** provides a common publishing abstraction.
- **Publisher adapters** contain platform-specific publishing logic.

### Why this architecture?

It directly follows the capstone flow:

```text
Ingest
  ↓
Store
  ↓
Generate
  ↓
Validate
  ↓
Review
  ↓
Schedule
  ↓
Publish through adapter
  ↓
Record publish history
```

This architecture separates the main responsibilities of the system:

- **Ingestion** stores the blog post as the single source of truth.
- **Generation** creates platform-specific variants using the stored post.
- **Validation** independently enforces platform constraints.
- **Review** ensures that unapproved content cannot be published.
- **Scheduling** determines when approved variants should be published.
- **Celery workers** execute publishing in the background.
- **SocialPublisher** separates business logic from platform-specific publishing APIs.
- **Publish history** records every publishing attempt and its result.

This separation keeps the system maintainable, testable, and resilient. It also allows publishing adapters to be changed without modifying the core business logic.

---

## 3. Data Model

The system requires the following core entities:

```text
Post
Platform
ConstraintProfile
Variant
ScheduleSlot
PublishAttempt
```

### Entity Relationships

```text
Post
 └── has many ──> Variant

Platform
 ├── has one ──> ConstraintProfile
 └── has many ──> Variant

Variant
 ├── belongs to ──> Post
 ├── belongs to ──> Platform
 └── has many ──> ScheduleSlot

ScheduleSlot
 └── has many ──> PublishAttempt
```

### Post

Represents the original blog post provided by the user.

```text
Post
├── id
├── source_type
├── source_url
├── content
├── title
├── created_at
└── updated_at
```

`source_type` identifies whether the post was provided as a URL or pasted Markdown.

The stored `content` is the single source of truth for variant generation.

### Platform

Represents a supported social media platform.

Initial platforms:

```text
telegram
x
linkedin
```

Fields:

```text
Platform
├── id
├── name
├── is_active
└── created_at
```

### ConstraintProfile

Defines the validation rules for a platform.

```text
ConstraintProfile
├── id
├── platform_id
├── max_length
├── tone
└── max_hashtags
```

Each constraint profile belongs to one platform.

The application validates variants against these rules independently of the LLM.

### Variant

Represents a platform-specific version of a stored post.

```text
Variant
├── id
├── post_id
├── platform_id
├── content
├── status
├── created_at
└── updated_at
```

A variant belongs to one `Post` and one `Platform`.

The initial status of a generated variant is:

```text
draft
```

### ScheduleSlot

Represents a scheduled publishing operation for an approved variant.

```text
ScheduleSlot
├── id
├── variant_id
├── scheduled_at
├── status
├── idempotency_key
├── created_at
└── updated_at
```

A schedule slot belongs to one variant.

The `idempotency_key` uniquely identifies a publishing operation.

### PublishAttempt

Records each attempt to publish a scheduled variant.

```text
PublishAttempt
├── id
├── schedule_slot_id
├── attempted_at
├── status
├── external_post_id
├── error_message
└── created_at
```

A schedule slot can have multiple publish attempts because publishing may be retried after failures.

Only one successful publication must exist for the same variant and scheduled slot.

### Publishing Attempt Example

```text
Variant #10
    │
    └── ScheduleSlot
            scheduled_at = 2026-08-25 10:00
            │
            ├── PublishAttempt #1
            │       └── FAILED
            │
            └── PublishAttempt #2
                    └── SUCCESS
```

This separation allows the system to record failures and retries while preventing duplicate successful publications.

---

## 4. Variant and Publishing Lifecycle

A generated variant follows a controlled lifecycle.

```text
                 ┌──────────┐
                 │  draft   │
                 └────┬─────┘
                      │
             ┌────────┴────────┐
             ▼                 ▼
        ┌──────────┐      ┌──────────┐
        │ approved │      │ rejected │
        └────┬─────┘      └──────────┘
             │
             ▼
        ┌───────────┐
        │ scheduled │
        └─────┬─────┘
              │
              ▼
        ┌───────────┐
        │ published │
        └───────────┘
```

### Variant Statuses

```text
draft
approved
rejected
scheduled
published
```

### Allowed Transitions

```text
draft
 ├── approve ──> approved
 │
 └── reject ───> rejected

approved
 └── schedule ──> scheduled

scheduled
 └── successful publish ──> published
```

The following transitions are not allowed:

```text
draft     → scheduled
draft     → published
rejected  → scheduled
rejected  → published
```

Only an approved variant can be scheduled.

---

## 5. Platform Constraint Profiles

Each social media platform has a constraint profile.

The LLM is instructed to follow these rules, but application validation remains responsible for enforcing them.

### Telegram

```text
Platform: telegram
Maximum Length: 4096 characters
Tone: informative and engaging
Maximum Hashtags: 5
```

### X

```text
Platform: x
Maximum Length: 280 characters
Tone: concise and engaging
Maximum Hashtags: 3
```

### LinkedIn

```text
Platform: linkedin
Maximum Length: 3000 characters
Tone: professional and informative
Maximum Hashtags: 5
```

### Constraint Validation Flow

```text
Stored Post
     │
     ▼
Variant Generation
     │
     ▼
Generated Variant
     │
     ▼
Constraint Validator
     │
     ├── Valid ───> draft / review
     │
     └── Invalid ──> reject generation result
                       or regenerate
```

Constraint validation is independent of the LLM.

---

## 6. SocialPublisher Interface

All publishing platforms communicate through a common abstraction.

The business layer must not depend directly on Telegram, X, or LinkedIn APIs.

Conceptually:

```python
class SocialPublisher:

    async def publish(
        self,
        content: str,
        idempotency_key: str,
    ):
        ...
```

The concrete implementations are:

```text
SocialPublisher
├── TelegramPublisher
├── MockXPublisher
└── MockLinkedInPublisher
```

### TelegramPublisher

Communicates with the real Telegram API.

### MockXPublisher

Simulates publishing to X.

### MockLinkedInPublisher

Simulates publishing to LinkedIn.

Adding a new platform should primarily require creating a new publisher adapter rather than modifying the core publishing business logic.

---

## 7. Idempotency Strategy

Publishing must be safe to retry.

The same variant must not be published more than once for the same scheduled slot.

Each publishing operation receives a unique idempotency key.

```text
Variant ID + Schedule Slot ID
             │
             ▼
      Idempotency Key
```

Example:

```text
Variant ID: 10
Schedule Slot ID: 25

Idempotency Key:
variant:10:schedule:25
```

The idempotency key is stored in the database and must be unique.

```text
UNIQUE(idempotency_key)
```

### Retry Flow

```text
Scheduled Variant
        │
        ▼
Create / Find Publish Operation
        │
        ▼
Check Idempotency Key
        │
        ├── Already Successfully Published
        │       │
        │       └── Stop
        │
        └── Not Successfully Published
                │
                ▼
             Publish
                │
                ├── Success ──> Record SUCCESS
                │
                └── Failure ──> Record FAILURE
                                  │
                                  ▼
                                Retry
```

A failed publishing operation may be retried, but retries must not create a second successful publication for the same variant and schedule slot.

---

## 8. API Surface

The REST API will be versioned under:

```text
/api/v1
```

### Posts

```http
POST /api/v1/posts
GET  /api/v1/posts
GET  /api/v1/posts/{post_id}
```

A post can be created using either:

```json
{
  "source_type": "markdown",
  "content": "# My Blog Post"
}
```

or:

```json
{
  "source_type": "url",
  "source_url": "https://example.com/blog-post"
}
```

### Variant Generation

```http
POST /api/v1/posts/{post_id}/generate
GET  /api/v1/posts/{post_id}/variants
GET  /api/v1/variants/{variant_id}
PUT  /api/v1/variants/{variant_id}
```

### Review Workflow

```http
POST /api/v1/variants/{variant_id}/approve
POST /api/v1/variants/{variant_id}/reject
```

### Scheduling

```http
POST /api/v1/variants/{variant_id}/schedule
GET  /api/v1/schedules
```

### Publish History

```http
GET /api/v1/publish-history
GET /api/v1/publish-history/{publish_attempt_id}
```

---

## 9. Technology Decisions

### Backend

- Python
- FastAPI
- Pydantic

### Database

- PostgreSQL
- SQLAlchemy

### Background Processing

- Celery
- Celery Beat
- Redis

### AI Integration

- LangChain
- Mistral AI

### Publishing

- Telegram API
- Mock X Publisher
- Mock LinkedIn Publisher

### Infrastructure

- Docker
- Docker Compose
- uv

### Testing

- Pytest
- pytest-asyncio
- HTTPX

LangGraph is not part of the initial implementation. It may be introduced later if the AI workflow requires a stateful multi-step graph.

---

## 10. Explicit Non-Goals

The initial version of Social Media Studio will not include:

- Real Instagram publishing
- Real X publishing
- Real LinkedIn publishing
- Image generation
- Analytics
- Engagement tracking
- Multi-tenancy

The project focuses on transforming blog posts into validated social media variants, reviewing them, scheduling approved variants, and publishing them reliably.

---

## 11. Phase 1 Completion Criteria

Phase 1 is complete when the following design decisions are documented:

- [x] Problem definition
- [x] Core architecture
- [x] Core responsibilities
- [x] Data model
- [x] Entity relationships
- [x] Variant lifecycle
- [x] Platform constraint profiles
- [x] SocialPublisher abstraction
- [x] Idempotency strategy
- [x] API surface
- [x] Technology decisions
- [x] Explicit non-goals

The next phase begins only after this design is reviewed and accepted as the implementation blueprint.
