# GYM-IT System - Architecture Documentation

> **Course Project**: Gym Management System  
> **Architecture**: Microservices-based Web Application  
> **Deployment**: Docker & Kubernetes

---

## Executive Summary

The **GYM-IT System** is a comprehensive gym management platform built using microservices architecture. It manages user authentication, tournament operations, leaderboards, and administrative functions with scalability and security as core design principles.

**Key Features**: User Management, Tournament Brackets, Leaderboards, Role-Based Access, Real-time Notifications

---

## System Architecture Overview

### Architecture Diagram

```
┌─────────────────────────────────────────────────────┐
│              CLIENT LAYER (Browser/Mobile)          │
└──────────────────────┬──────────────────────────────┘
                       │ HTTPS
                       ▼
┌──────────────────────────────────────────────────────┐
│        API GATEWAY (Port 8000)                       │
│    Routing | Auth | Rate Limiting | Caching         │
└────┬─────────┬──────────┬──────────────┬────────────┘
     │         │          │              │
     ▼         ▼          ▼              ▼
┌─────────┐ ┌──────┐ ┌──────────┐ ┌──────────────┐
│  Auth   │ │ User │ │Tournament│ │Notification  │
│Service  │ │Service│ │ Service  │ │   Service    │
│(8001)   │ │(8002)│ │ (8003)   │ │   (8004)     │
└────┬────┘ └──┬───┘ └────┬─────┘ └──────┬───────┘
     │         │          │               │
     ▼         ▼          ▼               ▼
┌─────────┐ ┌──────┐ ┌──────────┐    ┌──────┐
│Auth DB  │ │User  │ │Tournament│    │Redis │
│PostgreSQL│ │DB    │ │  DB      │    │Cache │
└─────────┘ └──────┘ └──────────┘    └──────┘
```

**Code Reference**: [`docker-compose.microservices.yml`](docker-compose.microservices.yml)

---

## Microservices Design

### 1. API Gateway (`services/api-gateway/src/app.py`)
- **Purpose**: Single entry point, request routing, load balancing
- **Key Features**: Rate limiting, authentication check, request logging
- **Routes**: `/api/auth/*`, `/api/users/*`, `/api/tournaments/*`

### 2. Auth Service (`services/auth-service/src/api.py`)
- **Purpose**: User authentication and JWT token management
- **Endpoints**: `/login`, `/register`, `/verify-token`
- **Security**: Password hashing (bcrypt), JWT tokens (HS256)
- **Database**: PostgreSQL with User model

### 3. User Service (`services/user-service/src/api.py`)
- **Purpose**: User profile management and membership tracking
- **Endpoints**: `/users`, `/users/<id>`, `/memberships`
- **Features**: CRUD operations, role management, profile updates

### 4. Tournament Service (`services/tournament-service/src/api.py`)
- **Purpose**: Tournament and match management, leaderboard calculation
- **Endpoints**: `/tournaments`, `/matches`, `/leaderboard`
- **Features**: Bracket generation, match tracking, points calculation
- **Complex Logic**: `generate_bracket()` - Lines 450-520

### 5. Notification Service (`services/notification-service/src/api.py`)
- **Purpose**: Real-time notifications and event broadcasting
- **Technology**: WebSocket support, Redis pub/sub
- **Use Cases**: Match updates, tournament announcements

---

## Technology Stack

### Backend
| Technology | Purpose | Version |
|------------|---------|---------|
| Python | Backend Language | 3.9+ |
| Flask | Web Framework | 2.3.0 |
| PostgreSQL | Database | 13+ |
| Redis | Caching/Sessions | 7.0+ |
| Flask-JWT-Extended | Authentication | 4.5.0 |

### Frontend
| Technology | Purpose |
|------------|---------|
| HTML5/CSS3 | UI Structure |
| JavaScript | Interactivity |
| Bootstrap 5 | Styling |
| Font Awesome | Icons |

### Infrastructure
| Technology | Purpose |
|------------|---------|
| Docker | Containerization |
| Kubernetes | Orchestration |
| NGINX | Reverse Proxy/Ingress |

**Code Reference**: [`requirements.txt`](services/*/requirements.txt) for dependencies

---

## Database Architecture

### Database-Per-Service Pattern
Each microservice has its own PostgreSQL database for data isolation:
- `auth_db`: User credentials, tokens
- `user_db`: User profiles, memberships  
- `tournament_db`: Tournaments, matches, leaderboard

### Key Tables

**Auth Service** (`services/auth-service/src/models.py`):
```sql
User: id, username, email, password_hash, role, created_at
```

**Tournament Service** (`services/tournament-service/src/models.py`):
```sql
Tournament: id, name, type, status, start_date, max_participants
Match: id, tournament_id, round, player1_id, player2_id, winner_id
Leaderboard: user_id, points, tournaments_won, win_rate
```

---

## Security Implementation

### 1. Authentication Flow
```
User Login → Credentials Validation → JWT Token Generation → 
Token Storage (Browser) → Token Verification → Authorized Access
```

**Code**: `services/auth-service/src/api.py` - Lines 145-180

### 2. JWT Token Structure
- **Algorithm**: HS256
- **Expiration**: 1 hour
- **Payload**: user_id, username, role, exp
- **Secret**: Environment variable `JWT_SECRET_KEY`

### 3. Role-Based Access Control (RBAC)
| Role | Permissions |
|------|-------------|
| admin | Full system access, user management, reports |
| trainer | Tournament management, user viewing |
| member | Own profile, tournament participation |

**Implementation**: `static/js/auth.js` - `requireAuth()` function

### 4. Security Features
- ✅ Password hashing with bcrypt (10 rounds)
- ✅ JWT-based stateless authentication
- ✅ HTTPS/TLS for all communications
- ✅ SQL injection prevention (ORM parameterization)
- ✅ XSS protection (input sanitization)
- ✅ Rate limiting on API Gateway
- ✅ CORS configuration
- ✅ Secrets management (environment variables)

---

## Scalability & Deployment

### Kubernetes Architecture

**Auto-Scaling Configuration** (5x Growth Capacity):
| Service | Min Replicas | Max Replicas | Trigger |
|---------|--------------|--------------|---------|
| API Gateway | 5 | 15 | CPU 70% |
| Auth Service | 3 | 10 | CPU 70% |
| User Service | 3 | 10 | CPU 70% |
| Tournament Service | 5 | 15 | CPU 70% |
| Notification Service | 3 | 10 | CPU 70% |

**Deployment Files**: `k8s/production/` directory
- Deployments with HorizontalPodAutoscaler
- Services for internal communication
- Ingress for external access
- ConfigMaps and Secrets for configuration

**Deployment**:
```bash
cd k8s/production
./deploy.sh
```

**Code Reference**: `k8s/production/*.yaml` files

---

## Code Structure

```
GYM-IT-System/
├── services/
│   ├── api-gateway/        # Request routing
│   ├── auth-service/       # Authentication
│   ├── user-service/       # User management
│   ├── tournament-service/ # Tournaments & matches
│   └── notification-service/ # Real-time updates
├── static/
│   ├── css/               # Stylesheets
│   ├── js/                # Frontend logic (auth, tournaments, leaderboard)
│   └── *.html             # UI pages
├── k8s/production/        # Kubernetes manifests
└── docker-compose.microservices.yml
```

---

## Key Features with Code References

### 1. User Registration & Authentication
**Flow**: Register → Email validation → Password hash → JWT token
**Code**: 
- Backend: `services/auth-service/src/api.py` - Lines 95-130
- Frontend: `static/js/auth.js` - `login()` function
- UI: `static/login.html`

### 2. Tournament Bracket Generation
**Algorithm**: Single/double elimination bracket creation
**Code**: `services/tournament-service/src/api.py` - Lines 450-520
**Features**: Automatic pairing, bye rounds, winner advancement

### 3. Leaderboard Calculation
**Metrics**: Points, win rate, tournament wins
**Code**: `services/tournament-service/src/api.py` - Lines 745-800
**Display**: `static/js/leaderboard.js` with role-based filtering

---

## Deployment Instructions

### Local Development
```bash
# Start all services
docker-compose -f docker-compose.microservices.yml up -d

# Access application
http://localhost:8000
```

### Kubernetes Production
```bash
# Deploy to cluster
cd k8s/production
./deploy.sh

# Verify deployment
kubectl get pods -n gymit
kubectl get hpa -n gymit
```

**Prerequisites**: Kubernetes cluster, kubectl, Docker images built

---

## Performance & Testing

### Expected Performance
- **Concurrent Users**: 500-1000 (with auto-scaling)
- **Response Time**: <150ms (p95)
- **Throughput**: ~2,500 req/s
- **Uptime**: 99.9%

### Testing Checklist
- ✅ User registration/login
- ✅ Tournament creation/management
- ✅ Match recording/winner advancement
- ✅ Leaderboard calculation
- ✅ Role-based access control
- ✅ Authentication redirect
- ✅ API endpoint functionality

---

## Conclusion

The GYM-IT System demonstrates modern software architecture principles:
- **Scalability**: Microservices with Kubernetes auto-scaling
- **Security**: JWT authentication, RBAC, encrypted communications
- **Maintainability**: Clear code structure, database isolation
- **Performance**: Caching, efficient queries, containerization

The system successfully handles gym management operations with production-grade architecture suitable for real-world deployment.

---

## References

**Documentation**:
- Full deployment guide: `k8s/production/README.md`
- Quick start: `k8s/production/QUICK_START.md`

**Code Repository**: All source code available in the project repository with detailed inline documentation.

---

*Document prepared for academic review - Course Project Submission*
