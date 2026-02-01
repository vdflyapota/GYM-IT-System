# GYM IT System: Project Schedule & Task Distribution

## 🚀 Microservices Architecture

This project has been migrated to a microservices architecture! See the comprehensive documentation:

- **[Microservices Overview](MICROSERVICES.md)** - Complete guide to the microservices architecture
- **[Architecture Diagrams](ARCHITECTURE.md)** - Detailed system architecture and patterns
- **[Kubernetes Deployment](K8S_DEPLOYMENT.md)** - Production deployment guide

### Quick Start (Microservices)

```bash
# Check system requirements and port availability
./scripts/diagnose.sh

# Start all microservices
./scripts/start-microservices.sh

# Stop all microservices
./scripts/stop-microservices.sh

# Test the services
./scripts/test-microservices.sh

# Access the application
# API Gateway: http://localhost:8000
```

**Default Admin Login**:
- Email: `admin@gym.com`
- Password: `admin`

The admin account is automatically created on first launch to approve new user registrations.

**Troubleshooting**: If you encounter port conflict errors, run `./scripts/diagnose.sh` to identify which processes are using the required ports, then stop them before starting the microservices.

**Note**: If you were running the old monolithic version, the start script will automatically stop it to avoid port conflicts.

### Quick Start (Simple / Monolith)

**Prerequisites:** Python 3.8+, Node.js 16+ and npm

**Terminal 1 - Backend:**
```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Access:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Services (Microservices)

- **API Gateway** (Port 8000) - Entry point and request routing
- **Auth Service** (Port 8001) - Authentication and JWT generation
- **User Service** (Port 8002) - User management and profiles
- **Tournament Service** (Port 8003) - Tournament logic and brackets
- **Notification Service** (Port 8004) - Real-time notifications via WebSocket

Each service has its own PostgreSQL database and can be scaled independently.

---

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
