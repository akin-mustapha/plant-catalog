# Notification Feature — Design Documentation

## 1. Functional Requirements

| ID | Requirement |
|----|-------------|
| FR1 | User can access notification setup via a bell icon in the Plant Catalog app. |
| FR2 | User can create a notification with a name, description, schedule type, and up to 3 email contacts. |
| FR3 | User can choose between a cron-style schedule or a fixed interval (radio button, mutually exclusive). |
| FR4 | System sends an SNS subscription-confirmation email to each contact added. |
| FR5 | User can edit their existing notification (name, description, schedule/interval, contacts). |
| FR6 | v1 supports exactly one notification per user; the bell icon always opens that single record (create-if-absent, else edit). |
| FR7 | System automatically dispatches the notification message when its schedule comes due, with no manual trigger. |
| FR8 | System records the outcome (success/failure) of every dispatch attempt. |
| FR9 | The notification feature is generic — not coupled to "plant" as an entity — so other projects can reuse the same tables, Lambda, and topic pattern. |

## 2. Non-Functional Requirements

| ID | Requirement |
|----|-------------|
| NFR1 | **Reusability** — no plant-specific fields in the core schema; `notification_type` is the only per-project customization point. |
| NFR2 | **Reliability** — dispatch is idempotent; a retried Lambda invocation must not double-send. |
| NFR3 | **Observability** — every dispatch attempt (sent or failed) is logged with enough detail to debug a "why didn't I get this" report. |
| NFR4 | **Cost efficiency** — a single scheduled Lambda polls all due notifications, avoiding per-notification EventBridge schedules. |
| NFR5 | **Timeliness** — a notification dispatches within one polling interval of its `next_run_date` (interval TBD, e.g. 15 min). |
| NFR6 | **Security** — Lambdas use least-privilege IAM scoped to the specific DynamoDB tables and SNS topic they need. |
| NFR7 | **Extensibility** — `user_id` is nullable in v1 (no auth yet) but present in the schema so multi-tenancy needs no migration later. |
| NFR8 | **Data integrity** — `contacts` is capped at 3 entries, enforced on write. |

## 3. System Context Diagram

```mermaid
flowchart TB
    user((User))
    plantapp[Plant Catalog App]
    otherapp[Other client apps]
    notifsys[[Notification System]]
    inbox[User's email inbox]

    user -->|configures reminder via bell icon| plantapp
    plantapp -->|create / edit notification config| notifsys
    otherapp -->|create / edit notification config| notifsys
    notifsys -->|publishes message| inbox
    inbox -->|read by| user
```

## 4. Container Diagram

```mermaid
flowchart TB
    subgraph Client
        ui[Plant App UI<br/>bell icon + form]
    end

    subgraph "Notification System"
        api[Config Lambda<br/>behind API Gateway]
        ddb[(DynamoDB<br/>notification_type / notification / notification_log)]
        eb[EventBridge rule<br/>fixed schedule]
        dispatcher[Dispatcher Lambda]
        sns[SNS Topic]
    end

    inbox[User's email inbox]

    ui -->|HTTPS| api
    api -->|read / write| ddb
    api -->|sns:Subscribe per contact| sns
    eb -->|triggers on schedule| dispatcher
    dispatcher -->|query due notifications| ddb
    dispatcher -->|sns:Publish| sns
    dispatcher -->|write log entry| ddb
    sns -->|email| inbox
```

## 5. Component Diagram

**Dispatcher Lambda**

```mermaid
flowchart TB
    subgraph "Dispatcher Lambda"
        poller[Schedule Poller]
        renderer[Template Renderer]
        publisher[SNS Publisher]
        recompute[Next-Run Calculator]
        logger[Log Writer]
    end

    ddbIn[(notification table<br/>GSI: status + next_run_date)]
    ddbOut[(notification table)]
    ddbLog[(notification_log table)]

    poller -->|query due items| ddbIn
    poller --> renderer
    renderer --> publisher
    publisher -->|result| logger
    publisher -->|on success| recompute
    recompute -->|update next_run_date / status| ddbOut
    logger -->|write entry| ddbLog
```

**Config Lambda**

```mermaid
flowchart TB
    subgraph "Config Lambda"
        validator[Request Validator]
        crud[Notification CRUD Handler]
        subman[Subscription Manager]
    end

    ddb[(notification table)]
    sns[SNS Topic]

    validator --> crud
    crud -->|write record| ddb
    crud -->|per contact email| subman
    subman -->|sns:Subscribe| sns
```

## 6. ER Model

```mermaiderDiagram
    NOTIFICATION_TYPE ||--o{ NOTIFICATION : defines
    NOTIFICATION ||--o{ NOTIFICATION_LOG : produces

    NOTIFICATION_TYPE {
        string type_id PK
        string name
        string description
        string created_date
    }

    NOTIFICATION {
        string notification_id PK
        string user_id "nullable, v1 placeholder"
        string type_id FK
        string name
        string description
        string schedule "cron syntax, nullable"
        string interval "nullable"
        string next_run_date
        string status "ACTIVE or PAUSED"
        string topic_arn
        list contacts "max 3, email + subscription_arn"
    }

    NOTIFICATION_LOG {
        string notification_id PK
        string sent_at SK
        string status "SENT or FAILED"
        string sns_message_id
        string error
        string scheduled_for
    }
```

**Note:** `NOTIFICATION` also needs a GSI on `status` (PK) + `next_run_date` (SK) — this is the query the Dispatcher Lambda uses every polling cycle. Not expressible in the ER diagram above but essential to the schema.

## 7. Sequence Diagram — Notification Setup

```mermaid
sequenceDiagram
    actor User
    participant UI as Plant App UI
    participant API as Config Lambda
    participant DDB as DynamoDB
    participant SNS as SNS Topic
    participant Inbox as User's email inbox

    User->>UI: Tap bell icon
    UI->>User: Show notification form
    User->>UI: Submit name, description, schedule/interval, up to 3 emails
    UI->>API: POST /notifications
    API->>API: Validate input (max 3 contacts, valid cron/interval)
    API->>DDB: Write notification record (status = ACTIVE)
    loop for each contact email
        API->>SNS: Subscribe(topic_arn, email)
        SNS->>Inbox: Send confirmation email
    end
    API-->>UI: 201 Created
    UI-->>User: "Saved — check your email to confirm"
    User->>Inbox: Open confirmation email
    User->>SNS: Click confirm link
    SNS->>SNS: Mark subscription Confirmed
```