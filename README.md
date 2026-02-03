# Authors:
# Danial - parzival or vdflyapota
# Yazan - yazan225
# Shattyk - Shhh09git
# Yeldana - personnna

# GYM IT System - Microservices Architecture

> A comprehensive gym management system with tournament support, leaderboards, and role-based access control.
>
> **Status**: ✅ Production Ready | **Architecture**: Microservices | **Deployment**: Docker, Kubernetes

## 🚀 Quick Start

```bash
# Start all microservices
./scripts/start-microservices.sh

# Access the application at http://localhost:8000
```

**Default Admin Credentials:**
- Email: `admin@gym.com`  
- Password: `admin`

---

## 📚 Documentation

Core documentation is organized in the `docs/` folder:

- **[Full Implementation Overview](FINAL_SUMMARY.md)** - Complete project summary and features
- **[Architecture & Design](docs/architecture/ARCHITECTURE.md)** - System architecture and patterns
- **[Microservices Guide](docs/guides/MICROSERVICES.md)** - Complete guide to each service
- **[Kubernetes Deployment](docs/guides/K8S_DEPLOYMENT.md)** - Production deployment
- **[Additional Guides](docs/guides/)** - Role-based UI, migration, tournament features, etc.
- **[Archived Documentation](docs/archived/)** - Legacy fix documents and notes

### Troubleshooting

- **Port Conflicts**: Run `./scripts/diagnose.sh` to identify and resolve port issues
- **Database Issues**: Services use separate PostgreSQL instances for isolation
- **Service Health**: Check individual service health endpoints at `http://localhost:PORT/healthz`

### Architecture Overview

```
┌─────────────────────────────────────┐
│      API Gateway (Port 8000)        │
│    Request routing & validation     │
└────────────┬────────────────────────┘
             │
     ┌───────┼────────┬──────────┐
     │       │        │          │
  ┌──▼─┐  ┌─▼──┐  ┌──▼──┐  ┌───▼──┐
  │Auth│  │User│  │Tour-│  │Notif-│
  │Svc │  │Svc │  │nament│ │Service│
  │    │  │    │  │Svc  │  │      │
  └─┬──┘  └─┬──┘  └──┬──┘  └───┬──┘
    │       │        │          │
  ┌─▼──┐  ┌─▼──┐  ┌─▼──┐   ┌──▼──┐
  │Auth│  │User│  │Tour│   │Redis│
  │ DB │  │ DB │  │ DB │   │Cache│
  └────┘  └────┘  └────┘   └─────┘
```

**Each microservice includes:**
- ✅ Independent database
- ✅ REST API endpoints
- ✅ Health check endpoint (`/healthz`)
- ✅ Docker containerization
- ✅ Kubernetes deployment configs

### Service Endpoints

| Service | Port | URL | Health Check |
|---------|------|-----|--------------|
| **API Gateway** | 8000 | http://localhost:8000 | http://localhost:8000/healthz |
| **Auth Service** | 8001 | http://localhost:8001 | http://localhost:8001/healthz |
| **User Service** | 8002 | http://localhost:8002 | http://localhost:8002/healthz |
| **Tournament Service** | 8003 | http://localhost:8003 | http://localhost:8003/healthz |
| **Notification Service** | 8004 | http://localhost:8004 | http://localhost:8004/healthz |

---

## 🛠️ Technology Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Flask 3.0, Python 3.11 |
| **Database** | PostgreSQL 16 |
| **Frontend** | Vanilla JavaScript, Bootstrap 5, HTML5 |
| **Containerization** | Docker & Docker Compose |
| **Orchestration** | Kubernetes (optional) |
| **Authentication** | JWT (JSON Web Tokens) |
| **Real-time** | WebSockets (Socket.IO) |
| **Caching** | Redis |

---

## 📋 Project Requirements

- Docker & Docker Compose
- Python 3.11+ (for local development)
- 5+ available ports (8000-8004)
- PostgreSQL 16 (or use Docker)
- 2GB+ RAM for all services

---

## 📁 Project Structure

```
gym-it-system/
├── README.md                          # This file
├── FINAL_SUMMARY.md                   # Complete implementation overview
├── LICENSE
├── Makefile
│
├── docs/                              # All documentation
│   ├── architecture/
│   │   └── ARCHITECTURE.md
│   ├── guides/
│   │   ├── MICROSERVICES.md
│   │   ├── K8S_DEPLOYMENT.md
│   │   └── ... (more guides)
│   └── archived/                      # Legacy documents
│
├── services/                          # Microservices
│   ├── api-gateway/
│   ├── auth-service/
│   ├── user-service/
│   ├── tournament-service/
│   └── notification-service/
│
├── static/                            # Frontend assets
│   ├── js/
│   ├── css/
│   └── *.html (pages)
│
├── scripts/                           # Automation
│   ├── start-microservices.sh
│   ├── stop-microservices.sh
│   └── test-microservices.sh
│
├── docker-compose.yml                 # Development
└── docker-compose.microservices.yml   # Microservices mode
```

---

## 🚀 Getting Started

### Prerequisites
- Install Docker Desktop
- Clone this repository
- Ensure ports 8000-8004 are available

### Run the Application

```bash
# Start all microservices
./scripts/start-microservices.sh

# Wait for services to initialize (~30 seconds)
# Then open http://localhost:8000 in your browser

# Login with:
# Email: admin@gym.com
# Password: admin
```

### Stop Services

```bash
./scripts/stop-microservices.sh
```

### View Logs

```bash
# See all running containers
docker-compose -f docker-compose.microservices.yml logs -f

# See specific service logs
docker-compose -f docker-compose.microservices.yml logs -f auth-service
```

---

## 🔧 Development
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
