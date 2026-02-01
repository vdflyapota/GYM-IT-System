# Microservices Architecture Diagram

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Load Balancer                            │
│                  (Kubernetes Ingress / NGINX)                    │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API Gateway (Port 8000)                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  • Route incoming requests to microservices              │  │
│  │  • JWT token validation (shared secret)                  │  │
│  │  • CORS handling                                         │  │
│  │  • Static file serving                                   │  │
│  │  • Request/Response logging                              │  │
│  └──────────────────────────────────────────────────────────┘  │
└──┬──────────┬──────────────┬──────────────┬────────────────────┘
   │          │              │              │
   ▼          ▼              ▼              ▼
┌─────────┐ ┌─────────┐  ┌──────────┐  ┌──────────────┐
│  Auth   │ │  User   │  │Tournament│  │Notification  │
│ Service │ │ Service │  │ Service  │  │  Service     │
│ :8001   │ │ :8002   │  │ :8003    │  │  :8004       │
└────┬────┘ └────┬────┘  └────┬─────┘  └──────┬───────┘
     │           │             │                │
     │           │             │                │
┌────▼──────┐┌───▼──────┐┌────▼───────┐        │
│ Auth DB   ││ User DB  ││Tournament  │        │
│PostgreSQL ││PostgreSQL││   DB       │        │
│  :5433    ││  :5434   ││PostgreSQL  │        │
└───────────┘└──────────┘│  :5435     │        │
                         └────────────┘        │
                                               │
                         ┌─────────────────────▼───┐
                         │      Redis :6379         │
                         │  (Pub/Sub & Caching)     │
                         └──────────────────────────┘
```

## Service Communication Patterns

### 1. Synchronous REST Communication

```
Client → API Gateway → Auth Service
                    → User Service
                    → Tournament Service
                    → Notification Service
```

**Example Flow: User Registration**
```
1. Client sends POST /api/auth/register to API Gateway
2. API Gateway routes to Auth Service
3. Auth Service:
   a. Creates auth record in auth-db
   b. Calls User Service POST /api/users/create
4. User Service creates profile in user-db
5. Response flows back through gateway to client
```

### 2. Asynchronous Event-Driven Communication

```
Tournament Service → Redis Pub/Sub → Notification Service → WebSocket Clients
```

**Example Flow: Tournament Update**
```
1. Tournament Service publishes event to Redis
2. Notification Service subscribes to Redis channel
3. Notification Service broadcasts via WebSocket
4. Connected clients receive real-time update
```

## Database Per Service Pattern

Each microservice has its own database to ensure:
- **Data Isolation**: Services don't directly access other services' data
- **Independent Scaling**: Each database can be scaled independently
- **Technology Flexibility**: Different databases can use different technologies
- **Fault Isolation**: Database failure affects only one service

### Database Schema Ownership

**Auth Service (auth-db)**
```sql
Table: users
- id (PK)
- email (unique)
- password_hash
- role
- is_active
- is_approved
- is_banned
```

**User Service (user-db)**
```sql
Table: users
- id (PK, same as auth-db)
- email
- full_name
- role
- is_approved
- is_banned
- is_root_admin
```

**Tournament Service (tournament-db)**
```sql
Table: tournaments
- id (PK)
- name
- start_date
- max_participants
- tournament_type
- status

Table: participants
- id (PK)
- tournament_id (FK)
- user_id (reference to user service)
- name
- seed

Table: brackets
- id (PK)
- tournament_id (FK)
- round
- match_number
- participant1_id (FK)
- participant2_id (FK)
- winner_id (FK)
- score
```

## Authentication & Authorization Flow

```
┌──────────┐
│  Client  │
└────┬─────┘
     │ 1. POST /api/auth/login
     │    {email, password}
     ▼
┌──────────────┐
│ API Gateway  │
└────┬─────────┘
     │ 2. Route to Auth Service
     ▼
┌──────────────┐
│Auth Service  │────► 3. Validate credentials
└────┬─────────┘      4. Generate JWT token
     │                   {user_id, role, email}
     │ 5. Return JWT
     ▼
┌──────────┐
│  Client  │────► 6. Store JWT
└────┬─────┘
     │ 7. Subsequent requests with
     │    Authorization: Bearer <JWT>
     ▼
┌──────────────┐
│ API Gateway  │────► 8. Validate JWT (shared secret)
└────┬─────────┘
     │ 9. Route to appropriate service
     │    with JWT claims
     ▼
┌──────────────┐
│Any Service   │────► 10. Use JWT claims for authorization
└──────────────┘         (role, user_id)
```

## Service Discovery

### Development (Docker Compose)
- Services discover each other using container names
- Docker's internal DNS resolves service names to container IPs
- Example: `http://auth-service:8001`

### Production (Kubernetes)
- Kubernetes Services provide stable DNS names
- Service discovery via Kubernetes DNS
- Example: `http://auth-service.gymit-microservices.svc.cluster.local:8001`
- Can be shortened to: `http://auth-service:8001` within same namespace

## Load Balancing

### API Gateway Level
- Multiple API Gateway instances (replicas: 3)
- Kubernetes Service distributes load across pods
- Round-robin or least-connection algorithms

### Service Level
- Each microservice can be scaled independently
- Kubernetes manages pod distribution
- Example scaling:
  ```bash
  kubectl scale deployment tournament-service --replicas=5
  ```

## Resilience Patterns

### 1. Health Checks
All services expose `/healthz` endpoint:
- Liveness probe: Service is alive
- Readiness probe: Service is ready to accept traffic

### 2. Circuit Breaker (Future Enhancement)
Prevent cascading failures:
```python
# Example with circuit breaker
if circuit_breaker.is_open("user-service"):
    return cached_response()
else:
    try:
        response = call_user_service()
        circuit_breaker.record_success()
    except Exception:
        circuit_breaker.record_failure()
```

### 3. Retry Logic
Transient failure handling:
```python
@retry(stop=stop_after_attempt(3), wait=wait_exponential())
def call_external_service():
    # Service call
    pass
```

### 4. Graceful Degradation
- If User Service is down, Auth Service can still authenticate
- Tournament listing can work without user profile enrichment

## Monitoring & Observability

### Metrics (Prometheus)
```
# Service-level metrics
service_requests_total{service="auth-service"}
service_request_duration_seconds{service="auth-service"}
service_errors_total{service="auth-service"}

# Infrastructure metrics
database_connections{service="auth-service"}
redis_connection_pool{service="notification-service"}
```

### Logging (Structured JSON)
```json
{
  "timestamp": "2026-01-26T20:00:00Z",
  "service": "auth-service",
  "level": "INFO",
  "message": "User login successful",
  "user_id": 123,
  "correlation_id": "abc-123-def"
}
```

### Tracing (Future Enhancement)
Distributed tracing with OpenTelemetry:
```
Request ID: abc-123-def
├─ API Gateway (10ms)
├─ Auth Service (50ms)
│  └─ Database Query (40ms)
└─ User Service (30ms)
   └─ Database Query (25ms)
Total: 90ms
```

## Security Architecture

### 1. Defense in Depth
```
Internet → Load Balancer (TLS) → API Gateway (JWT) → Services (JWT validation)
```

### 2. Network Isolation
- Services communicate only through defined APIs
- Kubernetes Network Policies restrict pod-to-pod communication
- Databases not exposed externally

### 3. Secret Management
- Kubernetes Secrets for sensitive data
- Environment variables for configuration
- Consider HashiCorp Vault for production

### 4. API Security
- JWT tokens with expiration
- Role-based access control (RBAC)
- Rate limiting at gateway level
- CORS configuration

## Deployment Strategies

### Rolling Update
```
# Kubernetes automatically manages
# No downtime deployment
Old pods: [V1] [V1] [V1]
          ↓
Mixed:    [V1] [V1] [V2]
          ↓
Mixed:    [V1] [V2] [V2]
          ↓
New pods: [V2] [V2] [V2]
```

### Blue/Green Deployment
```
# Route traffic from old to new version
Blue (V1):  100% traffic → 0% traffic
Green (V2):   0% traffic → 100% traffic
```

### Canary Deployment
```
# Gradually shift traffic
V1: 100% → 90% → 50% → 0%
V2:   0% → 10% → 50% → 100%
```

## Scalability Strategy

### Horizontal Scaling
- Tournament Service: 3-10 replicas (high load expected)
- User Service: 2-5 replicas
- Auth Service: 2-5 replicas
- Notification Service: 2-5 replicas
- API Gateway: 3-10 replicas

### Vertical Scaling
- Database instances can be upgraded for more resources
- Redis can be scaled with clustering

### Database Scaling
- Read replicas for read-heavy services
- Connection pooling
- Caching frequently accessed data

## Migration Path from Monolith

### Phase 1: Strangler Fig Pattern
Keep monolith running while building services:
```
Client → API Gateway → New Services (gradually replacing)
                    → Monolith (legacy endpoints)
```

### Phase 2: Service Extraction
Extract one service at a time:
1. Auth Service (completed)
2. User Service (completed)
3. Tournament Service (completed)
4. Notification Service (completed)

### Phase 3: Data Migration
- Migrate data from monolith DB to service-specific DBs
- Ensure data consistency during transition
- Implement dual-write during migration period

### Phase 4: Retire Monolith
- All traffic through microservices
- Decommission monolith
- Archive monolith code

## Future Enhancements

1. **Service Mesh (Istio/Linkerd)**
   - Advanced traffic management
   - Mutual TLS between services
   - Distributed tracing
   - Circuit breaking

2. **Event Sourcing**
   - Maintain event log for audit
   - Replay events for debugging
   - Event-driven architecture

3. **CQRS (Command Query Responsibility Segregation)**
   - Separate read and write models
   - Optimized queries
   - Better scalability

4. **API Versioning**
   - Support multiple API versions
   - Graceful deprecation
   - Backward compatibility

5. **GraphQL Gateway**
   - Unified API layer
   - Client-driven queries
   - Reduced over-fetching
