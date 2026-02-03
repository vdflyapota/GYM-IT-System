# Tournament Service

Microservice for Tournament Management - part of GYM IT System.

**Owner:** Danial Rakhat  
**Architecture Responsibility:** Scalability & DevOps

## Features

- Tournament creation and management
- Bracket generation (single/double elimination)
- Match scheduling and scoring
- Tournament progression tracking

## Architecture

This is a **microservice** that runs independently on port **8002**.

### Service Communication

- **Auth Service** (port 8001): Validates user IDs for participants
- **Notification Service** (port 8004): Sends match start/completion notifications
- **Frontend** (port 3000): Consumes this service's API

## Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the service
uvicorn main:app --reload --port 8002
```

Service will be available at: `http://localhost:8002`
API Documentation: `http://localhost:8002/docs`

### Docker

```bash
# Build and run
docker-compose up --build

# Or using Docker directly
docker build -t tournament-service .
docker run -p 8002:8002 tournament-service
```

### Kubernetes

See `k8s/` directory for deployment manifests.

```bash
kubectl apply -f k8s/
```

## API Endpoints

- `GET /health` - Health check
- `POST /tournaments/` - Create tournament
- `GET /tournaments/` - List tournaments
- `GET /tournaments/{id}` - Get tournament
- `POST /tournaments/{id}/generate-bracket` - Generate bracket
- `GET /tournaments/{id}/bracket` - Get bracket tree
- `PUT /matches/{id}` - Update match
- `GET /matches/{id}` - Get match

## Database

- **Development:** SQLite (`tournament.db`)
- **Production:** PostgreSQL (set `DATABASE_URL` env variable)

## Environment Variables

- `DATABASE_URL` - Database connection string (default: `sqlite:///./tournament.db`)
- `PORT` - Service port (default: 8002)

## Scalability

- Designed for horizontal scaling
- Stateless service (can run multiple replicas)
- Kubernetes-ready with health checks
- Supports 5x growth (3-5 replicas recommended)

## Testing

```bash
# Test health endpoint
curl http://localhost:8002/health

# Create tournament
curl -X POST "http://localhost:8002/tournaments/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Tournament", "start_date": "2024-01-15T10:00:00", "max_participants": 8}'
```
