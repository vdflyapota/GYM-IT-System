# GYM-IT-System-CM0639-1
GYM IT-System (CM0639-1) repository - represents our project for the course SOFTWARE ARCHITECTURES (CM90) - a.a. 2025-26

# GYM IT System: Project Schedule & Task Distribution

## Team Members & Core Responsibilities
| Student | Core Domain (Vertical Slice) | Architectural Responsibility |
| :--- | :--- | :--- |
| **Danial Rakhat** | **Tournament Engine:** Brackets, Match Scheduling, Scoring Logic. | **Scalability & DevOps:** Dockerization, Kubernetes configuration, CI pipelines. |
| **Yazan Slaila** | **User Management:** Auth, Profiles, Roles, Staff Management. | **Security:** JWT implementation, AES-256 Encryption, RBAC Middleware. |
| **Yeldana Kadenova** | **Challenges & Leaderboards:** Real-time rankings, Point calculation. | **Simplicity & UI Architecture:** Shared UI Components, UX Standards, Frontend Routing. |
| **Shattyk Kuziyeva** | **Reporting & Notifications:** Dashboards, Email/Push Services, Logs. | **Fault Tolerance & Data:** Backup scripts, Load Testing, Database Reliability. |

---

## Phase 1: Architecture, Setup & Core Foundations (Week 1)
**Goal:** Initialize the repo, set up the environment, and establish communication standards.

| Assignee | Task / Issue | Definition of Done |
| :--- | :--- | :--- |
| **Danial** | **[Infra]** Containerization Setup | Create `Dockerfile` and `docker-compose.yml` for local dev. Ensure DB and API spin up. |
| **Yazan** | **[Security]** Auth Database Design | Design User/Role Schema. Implement Register/Login API with JWT generation. |
| **Yeldana** | **[UI]** Frontend Skeleton & Design System | Initialize React/Vue/Angular app. Create shared Layout (Sidebar/Header) and Theme (Colors/Fonts). |
| **Shattyk** | **[Data]** Database Migration System | Set up the ORM (Prisma/TypeORM/Sequelize) and create the initial migration scripts for all modules. |

## Phase 2: Core Feature Implementation (Weeks 2-3)
**Goal:** Getting the logic working. Everyone codes heavily in their specific module.

| Assignee | Task / Issue | Definition of Done |
| :--- | :--- | :--- |
| **Danial** | **[Backend]** Tournament Logic | API to create tournaments, generate bracket trees, and assign participants. |
| **Danial** | **[Frontend]** Tournament Setup UI | Create UI forms for Admins to configure tournament rules and dates (Max 2 clicks). |
| **Yazan** | **[Backend]** RBAC Middleware | Implement middleware that restricts endpoints based on Admin/Trainer/Member roles. |
| **Yazan** | **[Frontend]** Profile & Admin Panel | Create User Profile pages and the Admin "User Management" grid view. |
| **Yeldana** | **[Backend]** Leaderboard Logic | API to fetch aggregated scores. Optimize queries for speed (< 2s latency). |
| **Yeldana** | **[Frontend]** Live Leaderboard UI | Create a responsive Leaderboard component that auto-refreshes or uses WebSockets. |
| **Shattyk** | **[Backend]** Notification Service | Implement a micro-service or module that triggers emails/alerts when a match starts. |
| **Shattyk** | **[Frontend]** Activity Dashboard | Create the "Home" dashboard showing recent system activity and alerts. |

## Phase 3: Integration & Architectural Hardening (Week 4)
**Goal:** Connecting the modules and satisfying the specific Architecture Characteristics (Scalability, Fault Tolerance).

| Assignee | Task / Issue | Definition of Done |
| :--- | :--- | :--- |
| **Danial** | **[Scalability]** Kubernetes Deployment | Create K8s manifests (Deployment, Service, Ingress). Configure replicas for 5x growth handling. |
| **Yazan** | **[Security]** Data Encryption | Implement AES-256 encryption for sensitive fields (at rest) and enforce HTTPS (in transit). |
| **Yeldana** | **[Responsiveness]** UI Performance Tuning | Implement Lazy Loading for modules. Ensure Main Content Paint < 1 second. |
| **Shattyk** | **[Fault Tolerance]** Backup System | Write a script for automated daily DB backups and verify the Restoration process (RTO < 5 min). |

## Phase 4: Final Polish & Testing (Week 5)
**Goal:** Ensuring the professor sees the quality and reliability.

| Assignee | Task / Issue | Definition of Done |
| :--- | :--- | :--- |
| **Danial** | **[Docs]** Architecture Documentation | Finalize C4 diagrams and API documentation (Swagger/OpenAPI). |
| **Yazan** | **[QA]** Security Audit | Attempt SQL injection/XSS on peers' code and patch vulnerabilities. |
| **Yeldana** | **[UX]** Usability Polish | Fix UI alignment issues. Ensure "Simplicity" metric (max 2 clicks) is met for key flows. |
| **Shattyk** | **[Testing]** Load Testing | Run JMeter/K6 tests simulating 1,000 concurrent users. Generate performance report. |


erDiagram
    %% USER MANAGEMENT MODULE (Owned by Yazan)
    USERS {
        uuid id PK
        string email UK "Indexed"
        string password_hash "AES-256 Encrypted"
        string role "ENUM: ADMIN, TRAINER, MEMBER"
        timestamp created_at
    }
    PROFILES {
        uuid id PK
        uuid user_id FK
        string full_name
        string phone_number "Encrypted"
        json preferences
    }

    %% TOURNAMENT MODULE (Owned by Danial)
    TOURNAMENTS {
        uuid id PK
        string name
        timestamp start_date
        timestamp end_date
        string status "ENUM: PENDING, ACTIVE, FINISHED"
        int max_participants
    }
    MATCHES {
        uuid id PK
        uuid tournament_id FK
        uuid player_1_id FK
        uuid player_2_id FK
        uuid winner_id FK
        int round_number
        json score_metadata
    }

    %% CHALLENGES & LEADERBOARDS MODULE (Owned by Yeldana)
    CHALLENGES {
        uuid id PK
        string name
        string metric "ENUM: REPS, TIME, WEIGHT"
        int points_awarded
    }
    SCORES {
        uuid id PK
        uuid user_id FK
        uuid challenge_id FK
        float value
        timestamp submitted_at
        boolean verified
    }
    %% Note: Leaderboard is a View/Query, not a table

    %% REPORTING & NOTIFICATIONS MODULE (Owned by Shattyk)
    NOTIFICATIONS {
        uuid id PK
        uuid user_id FK
        string message
        boolean is_read
        timestamp sent_at
    }
    AUDIT_LOGS {
        uuid id PK
        uuid actor_id FK
        string action
        string target_entity
        timestamp occurred_at
    }

    %% RELATIONSHIPS
    USERS ||--|| PROFILES : "has"
    USERS ||--o{ SCORES : "submits"
    USERS ||--o{ NOTIFICATIONS : "receives"
    TOURNAMENTS ||--|{ MATCHES : "contains"
    CHALLENGES ||--o{ SCORES : "tracks"
