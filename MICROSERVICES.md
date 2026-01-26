# GYM IT System - Microservices Architecture

## Overview

This project has been migrated from a monolithic Flask application to a microservices architecture. The application is now split into independent services that communicate via REST APIs and message queues.

## Architecture

### Service Overview

```
┌─────────────────┐
│   API Gateway   │  (Port 8000) - Entry point, routes requests
└────────┬────────┘
         │
    ┌────┴─────────────────────────────────────┐
    │                                           │
┌───▼────────┐  ┌──────────┐  ┌─────────────┐ │
│Auth Service│  │User Svc  │  │Tournament   │ │
│(Port 8001) │  │(Port 8002)  │Service      │ │
│            │  │          │  │(Port 8003)  │ │
└─────┬──────┘  └────┬─────┘  └──────┬──────┘ │
      │              │                │        │
   ┌──▼──────────────▼────────────────▼────┐   │
   │         PostgreSQL Databases         │   │
   │  (auth-db, user-db, tournament-db)   │   │
   └──────────────────────────────────────┘   │
                                               │
                              ┌────────────────▼──┐
                              │Notification Service│
                              │  (Port 8004)       │
                              │  WebSocket/Events  │
                              └────────┬───────────┘
                                       │
                              ┌────────▼───────┐
                              │  Redis Pub/Sub │
                              └────────────────┘
```

### Services

1. **API Gateway** (Port 8000)
   - Entry point for all client requests
   - Routes requests to appropriate microservices
   - Handles static file serving
   - Load balancing capability

2. **Auth Service** (Port 8001)
   - User authentication and authorization
   - JWT token generation and validation
   - Password management
   - Database: `auth-db` (PostgreSQL)

3. **User Service** (Port 8002)
   - User profile management
   - User approval and ban management
   - Role-based access control
   - Database: `user-db` (PostgreSQL)

4. **Tournament Service** (Port 8003)
   - Tournament creation and management
   - Bracket generation
   - Participant management
   - Match scheduling and scoring
   - Database: `tournament-db` (PostgreSQL)

5. **Notification Service** (Port 8004)
   - Real-time notifications via WebSocket
   - Event broadcasting
   - Redis pub/sub for message distribution

### Database Architecture

Each service has its own PostgreSQL database to ensure data isolation:

- **auth-db**: Stores authentication credentials and basic user data
- **user-db**: Stores extended user profiles and permissions
- **tournament-db**: Stores tournaments, participants, and brackets

### Inter-Service Communication

- **REST APIs**: Synchronous communication between services
- **Redis Pub/Sub**: Asynchronous event-driven communication for notifications
- **Shared JWT Secret**: Services validate JWT tokens independently

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Git

### Running the Microservices

1. **Clone the repository**:
   ```bash
   git clone https://github.com/vdflyapota/GYM-IT-System.git
   cd GYM-IT-System
   ```

2. **Start all services**:
   ```bash
   docker-compose -f docker-compose.microservices.yml up --build
   ```

3. **Access the application**:
   - API Gateway: http://localhost:8000
   - Auth Service: http://localhost:8001
   - User Service: http://localhost:8002
   - Tournament Service: http://localhost:8003
   - Notification Service: http://localhost:8004

### Environment Variables

Create a `.env` file in the project root:

```env
# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# Admin Bootstrap
ADMIN_EMAIL=admin@gym.it
ADMIN_PASSWORD=securepassword123

# Environment
ENV=development
CORS_ORIGINS=*
```

### Health Checks

Each service exposes a health check endpoint:

- API Gateway: `GET http://localhost:8000/healthz`
- Auth Service: `GET http://localhost:8001/healthz`
- User Service: `GET http://localhost:8002/healthz`
- Tournament Service: `GET http://localhost:8003/healthz`
- Notification Service: `GET http://localhost:8004/healthz`

## API Endpoints

### Auth Service (`/api/auth`)

- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login and get JWT token
- `POST /api/auth/validate` - Validate JWT token (internal use)

### User Service (`/api/users`)

- `GET /api/users/me` - Get current user profile (requires JWT)
- `GET /api/users/` - List all users (admin only)
- `GET /api/users/:id` - Get user by ID
- `PATCH /api/users/approve` - Approve a user (admin only)
- `PATCH /api/users/ban` - Ban a user (admin only)

### Tournament Service (`/api/tournaments`)

- `POST /api/tournaments/` - Create tournament (trainer/admin)
- `GET /api/tournaments/` - List all tournaments
- `GET /api/tournaments/:id` - Get tournament details
- `POST /api/tournaments/:id/participants` - Add participant
- `GET /api/tournaments/:id/participants` - List participants
- `GET /api/tournaments/:id/brackets` - Get tournament brackets

### Notification Service (`/api/notifications`)

- `POST /api/notifications/send` - Send notification to specific user
- `POST /api/notifications/broadcast` - Broadcast message to all users

## Development

### Running Individual Services

You can run individual services for development:

```bash
# Auth Service
cd services/auth-service
pip install -r requirements.txt
python -m src.app

# User Service
cd services/user-service
pip install -r requirements.txt
python -m src.app

# Tournament Service
cd services/tournament-service
pip install -r requirements.txt
python -m src.app

# Notification Service
cd services/notification-service
pip install -r requirements.txt
python -m src.app

# API Gateway
cd services/api-gateway
pip install -r requirements.txt
python -m src.app
```

### Service Discovery and Load Balancing

For production deployment:

1. **Kubernetes Deployment**: Use the manifests in `k8s/` directory
2. **Service Mesh**: Consider Istio or Linkerd for:
   - Service discovery
   - Load balancing
   - Circuit breaking
   - Observability

### Scaling Services

Scale individual services using Docker Compose:

```bash
docker-compose -f docker-compose.microservices.yml up --scale tournament-service=3
```

For Kubernetes:

```bash
kubectl scale deployment tournament-service --replicas=3
```

## Testing

### Unit Tests

Each service has its own test suite:

```bash
cd services/auth-service
pytest tests/

cd services/user-service
pytest tests/

cd services/tournament-service
pytest tests/
```

### Integration Tests

Test inter-service communication:

```bash
pytest integration-tests/
```

## Deployment

### Docker Compose (Development/Staging)

```bash
docker-compose -f docker-compose.microservices.yml up -d
```

### Kubernetes (Production)

```bash
kubectl apply -f k8s/namespaces/
kubectl apply -f k8s/databases/
kubectl apply -f k8s/services/
kubectl apply -f k8s/gateway/
```

## Monitoring and Observability

- **Health Checks**: Each service exposes `/healthz` endpoint
- **Logs**: Centralized logging via JSON logger
- **Metrics**: Prometheus metrics (can be added to each service)
- **Tracing**: Distributed tracing can be added via OpenTelemetry

## Security

### Authentication Flow

1. User logs in via API Gateway → Auth Service
2. Auth Service validates credentials and returns JWT token
3. Client includes JWT token in subsequent requests
4. API Gateway forwards token to services
5. Each service validates JWT independently

### Security Features

- **Distributed Authentication**: JWT tokens validated by all services
- **Separate Databases**: Data isolation per service
- **CORS Configuration**: Configurable CORS origins
- **Password Hashing**: Werkzeug security for password storage
- **HTTPS**: Enable in production (configure in gateway/load balancer)

## Migration from Monolith

The original monolithic application has been split as follows:

| Monolithic Module | New Service | Notes |
|-------------------|-------------|-------|
| `src/auth/` | auth-service | Authentication logic |
| `src/users/` | user-service | User management |
| `src/tournaments/` | tournament-service | Tournament logic |
| `src/notifications/` | notification-service | WebSocket events |
| `src/app.py` | api-gateway | Request routing |

## Troubleshooting

### Service Cannot Connect to Database

Check database health:
```bash
docker-compose -f docker-compose.microservices.yml ps
```

### Inter-Service Communication Failure

Check service logs:
```bash
docker-compose -f docker-compose.microservices.yml logs auth-service
docker-compose -f docker-compose.microservices.yml logs user-service
```

### Redis Connection Issues

Restart Redis:
```bash
docker-compose -f docker-compose.microservices.yml restart redis
```

## Future Enhancements

- [ ] API Gateway rate limiting
- [ ] Circuit breaker pattern for service resilience
- [ ] Event sourcing for audit logs
- [ ] GraphQL API layer
- [ ] Service mesh (Istio/Linkerd) implementation
- [ ] Distributed tracing (Jaeger/Zipkin)
- [ ] Centralized configuration management
- [ ] API versioning strategy

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## License

See [LICENSE](LICENSE) file.
