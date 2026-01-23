# Reporting & Fault Tolerance – Shattyk Kuziyeva

## Role in the System
I am responsible for system reliability, data safety, reporting, and fault tolerance.
This includes database reliability, backups, monitoring, notifications, and system stability.

---

## Database Architecture

### Current Setup
- ORM: SQLAlchemy
- Database: SQLite (`gym.db`)
- Connection handled in `database.py`
- Models are separated by domain:
  - `user_models.py`
  - `tournament_models.py`
  - `challenge_models.py`
  - `notification_models.py`

### Structure Design
- Central DB session management via `SessionLocal`
- Shared `Base` model for all schemas
- Modular model separation for scalability

---

## Migration Strategy (Planned)

### Current State
- No migration engine yet (Alembic not integrated)
- Schema changes currently handled manually via models

### Planned Migration Flow
1. Introduce Alembic
2. Auto-generate migrations from SQLAlchemy models
3. Version-controlled schema changes
4. Environment-based migrations (dev / prod)

**Goal:** Zero data loss during schema evolution.

---

## Fault Tolerance Strategy

### Data Safety
- Daily automated backups (planned)
- Backup storage separation
- Restore testing procedure

### Failure Handling
- Graceful DB connection handling
- Session rollback on failure
- Error isolation per service/module

---

## Backup System Design

### Planned Backup Flow
- Daily scheduled backup script
- Timestamped backup files
- Integrity validation
- Restore verification process

**RTO Goal:** < 5 minutes  
**RPO Goal:** < 24 hours

---

## Reporting System

### System Reporting
- Activity logs
- Error logs
- System health status
- Notification logs

### Admin Dashboards
- System activity
- Match events
- User activity
- Alerts

---

## Load Testing & Reliability

### Load Testing Plan
- Tooling: JMeter / K6
- Scenario: 1000 concurrent users
- Metrics:
  - Response time
  - Error rate
  - DB latency
  - Memory usage

### Stability Goals
- No data corruption
- No deadlocks
- No request loss
- Graceful degradation

---

## Architecture Quality Attributes
- Reliability
- Fault tolerance
- Data integrity
- Recoverability
- Observability
- Stability
