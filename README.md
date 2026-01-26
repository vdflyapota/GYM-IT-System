# GYM IT System: Project Schedule & Task Distribution

## Team Members & Core Responsibilities
| Student | Core Domain (Vertical Slice) | Architectural Responsibility |
| :--- | :--- | :--- |
| **Danial Rakhat** | **Tournament Engine:** Brackets, Match Scheduling, Scoring Logic. | **Scalability & DevOps:** Dockerization, Kubernetes configuration, CI pipelines. |
| **Yazan Slaila** | **User Management:** Auth, Profiles, Roles, Staff Management. | **Security:** JWT implementation, AES-256 Encryption, RBAC Middleware. |
| **Yeldana Kadenova** | **Challenges & Leaderboards:** Real-time rankings, Point calculation. | **Simplicity & UI Architecture:** Shared UI Components, UX Standards, Frontend Routing. |
| **Shattyk Kuziyeva** | **Reporting & Notifications:** Dashboards, Email/Push Services, Logs. | **Fault Tolerance & Data:** Backup scripts, Load Testing, Database Reliability. |

---

## Tournament Management Feature

The GYM IT System now includes a comprehensive tournament management feature that allows administrators and trainers to create and manage tournaments with bracket generation.

### Features

- **Tournament Creation**: Create tournaments with customizable names, participant limits, and tournament types
- **Participant Management**: Add participants to tournaments (supports both registered users and custom names)
- **Bracket Generation**: Automatic single-elimination bracket generation based on participants
- **Visual Bracket Display**: Interactive bracket visualization showing matchups and progression

### API Endpoints

- `POST /api/tournaments/` - Create a new tournament (requires trainer/admin role)
- `GET /api/tournaments/` - List all tournaments
- `GET /api/tournaments/<id>` - Get a specific tournament
- `PUT /api/tournaments/<id>/participants` - Add participants to a tournament (requires trainer/admin role)
- `GET /api/tournaments/<id>/participants` - Get participants for a tournament
- `GET /api/tournaments/<id>/bracket` - Generate and retrieve the tournament bracket

### Usage

1. Navigate to the Tournaments page from the dashboard
2. Click "New Tournament" to create a tournament
3. Fill in the tournament details (name, max participants, tournament type)
4. After creating, add participants using the "Add Participants" button
5. Once participants are added, view the generated bracket by clicking "View Bracket"

### Database Models

- **Tournament**: Stores tournament metadata (name, dates, status, type)
- **Participant**: Stores tournament participants with optional user linkage
- **Bracket**: Stores match information for bracket progression

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
