# Danial's Tasks Checklist

## 🚨 ВАЖНОЕ ИЗМЕНЕНИЕ: Микросервисная архитектура!

**Yazan сообщил:** Профессор требует микросервисную архитектуру, иначе проект не пройдет!

**Что это значит:**
- Вместо одного монолитного приложения будет несколько отдельных сервисов
- Каждый сервис работает на своем порту
- Tournament должен быть отдельным сервисом (`tournament-service`)

**👉 СМОТРИ ПОДРОБНЫЙ ГАЙД:** `DANIAL_TASKS_MICROSERVICES.md`

---

## 📊 Current Project Status

### What Yazan (Security/Auth) has done:
- ✅ User model with roles (`admin`, `trainer`, `member`)
- ✅ Register endpoint with password hashing (bcrypt)
- ❌ **NOT YET:** JWT tokens and login endpoint
- ❌ **NOT YET:** RBAC middleware for role-based access

### What this means for you:
- **You can work on Tournament features NOW** - endpoints don't need auth yet
- **When Yazan adds JWT/RBAC**, you'll need to integrate it (add `Depends(get_current_user)` to endpoints)
- **For now:** Tournament endpoints work without authentication
- **Frontend:** Uses mock tokens, will need to update when real auth is ready

### What's already in the project:
- ✅ Frontend structure ready (Layout, routing, design system)
- ✅ `Tournaments.jsx` page exists but is empty (placeholder)
- ✅ Dashboard links to tournaments
- ✅ React app with lazy loading (Phase 3 requirement already met!)

---

## ✅ Completed
- [x] Basic Tournament Backend API (`routers/tournaments.py`)
  - Create tournament endpoint
  - Generate bracket endpoint (simple pairing)

## 🔴 Phase 1: Containerization Setup (HIGH PRIORITY)

### Task: Create Dockerfile and docker-compose.yml
**Status:** ❌ NOT STARTED

**What to do:**
1. Create `Dockerfile` for FastAPI backend
2. Create `docker-compose.yml` with:
   - Backend service (FastAPI)
   - Frontend service (Vite dev server)
   - Database service (SQLite or PostgreSQL)
3. Ensure everything spins up with `docker-compose up`

**Files to create:**
- `Dockerfile`
- `docker-compose.yml`
- `.dockerignore` (optional but recommended)

**Definition of Done:**
- ✅ `docker-compose up` starts all services
- ✅ Backend accessible on port 8000
- ✅ Frontend accessible on port 3000
- ✅ Database works correctly

---

## 🟡 Phase 2: Tournament Logic & UI (IN PROGRESS)

### Task 1: Improve Tournament Backend Logic
**Status:** 🟡 PARTIALLY DONE (basic version exists, needs enhancement)

**Current state:**
- ✅ Basic tournament creation
- ✅ Simple bracket generation (pairs first 8 users)
- ❌ Missing: proper bracket tree structure
- ❌ Missing: match scheduling logic
- ❌ Missing: scoring logic
- ❌ Missing: tournament progression (rounds, finals)

**What to enhance:**
1. **Bracket Tree Generation:**
   - Implement proper elimination bracket (single/double elimination)
   - Support different tournament formats
   - Handle odd number of participants

2. **Match Scheduling:**
   - Schedule matches based on tournament dates
   - Handle match dependencies (winner advances)
   - Support multiple rounds

3. **Scoring Logic:**
   - Update match scores
   - Determine winners
   - Advance winners to next round
   - Handle tournament completion

**Files to modify:**
- `routers/tournaments.py` - Add new endpoints
- `models/tournament_models.py` - May need additional fields
- `schemas.py` - Add response schemas

**New endpoints needed:**
- `GET /tournaments` - List all tournaments
- `GET /tournaments/{id}` - Get tournament details with bracket
- `GET /tournaments/{id}/bracket` - Get bracket tree
- `PUT /matches/{id}` - Update match score/winner
- `POST /tournaments/{id}/register` - Register participant
- `GET /tournaments/{id}/schedule` - Get match schedule

**Note on Auth Integration:**
- Currently endpoints work without auth
- When Yazan adds JWT/RBAC, you'll need to:
  - Import `get_current_user` from auth module
  - Add `current_user: User = Depends(get_current_user)` to admin-only endpoints
  - Add role checks: `if current_user.role != "admin": raise HTTPException(...)`
  - Example: `create_tournament` should be admin-only

### Task 2: Tournament Setup UI (Frontend)
**Status:** ❌ NOT STARTED (only placeholder exists)

**Current state:**
- `frontend/src/pages/Tournaments.jsx` - Just shows "coming soon"
- Frontend routing already set up (`/tournaments` route exists)
- Design system ready (check `frontend/src/index.css`)
- Layout components ready (Sidebar, Header)
- Dashboard already links to tournaments page

**What to build:**
1. **Tournament Creation Form** (Max 2 clicks rule!)
   - Tournament name
   - Start date
   - Max participants
   - Tournament format (single/double elimination)
   - Submit button

2. **Tournament List View**
   - Show all tournaments
   - Status badges (PENDING, ACTIVE, FINISHED)
   - Quick actions (view, edit, start)

3. **Tournament Detail/Bracket View**
   - Visual bracket tree
   - Match cards with scores
   - Participant list
   - Actions: Generate bracket, Start tournament

**Files to create/modify:**
- `frontend/src/pages/Tournaments.jsx` - Main component (already exists, needs implementation)
- `frontend/src/pages/Tournaments.css` - Styling (already exists)
- May need new components in `frontend/src/components/`:
  - `TournamentForm.jsx` - Form for creating tournaments
  - `BracketView.jsx` - Visual bracket tree display
  - `MatchCard.jsx` - Individual match display

**API Integration:**
- Use `axios` (already in dependencies) to call backend
- Base URL: `http://localhost:8000` (or use proxy from `vite.config.js`)
- Example: `axios.get('/api/tournaments')` (proxy rewrites `/api` to backend)

**Definition of Done:**
- ✅ Admin can create tournament in max 2 clicks
- ✅ Form validates input
- ✅ Bracket visualization works
- ✅ UI matches design system

---

## 🟢 Phase 3: Kubernetes Deployment

### Task: Create K8s Manifests
**Status:** ❌ NOT STARTED

**What to create:**
1. `k8s/deployment.yaml` - Backend deployment
2. `k8s/deployment-frontend.yaml` - Frontend deployment
3. `k8s/service.yaml` - Services for backend/frontend
4. `k8s/ingress.yaml` - Ingress configuration
5. `k8s/configmap.yaml` - Configuration (optional)
6. `k8s/secret.yaml` - Secrets (optional)

**Requirements:**
- Configure replicas for 5x growth handling (e.g., 3-5 replicas)
- Health checks (liveness/readiness probes)
- Resource limits
- Horizontal Pod Autoscaler (HPA) if needed

**Definition of Done:**
- ✅ All manifests created
- ✅ Can deploy to K8s cluster
- ✅ Services accessible
- ✅ Replicas work correctly

---

## 🔵 Phase 4: Architecture Documentation

### Task: Finalize Architecture Documentation
**Status:** ❌ NOT STARTED

**What to create:**
1. **C4 Diagrams:**
   - System Context diagram
   - Container diagram
   - Component diagram (for Tournament module)
   - Deployment diagram

2. **API Documentation:**
   - Ensure Swagger/OpenAPI is complete
   - Add detailed descriptions to endpoints
   - Document request/response examples

3. **Architecture Decision Records (ADRs):**
   - Document key decisions for Tournament Engine
   - Document scalability decisions

**Files to create:**
- `docs/architecture/` folder
- `docs/architecture/c4-diagrams.md` or images
- `docs/architecture/adr/` folder

**Definition of Done:**
- ✅ C4 diagrams created
- ✅ API docs complete in Swagger
- ✅ ADRs documented

---

## 📝 Recommended Workflow

### For each task:
1. Create a feature branch: `git checkout -b feature/task-name`
2. Implement the feature
3. Test locally
4. Commit with clear message: `git commit -m "feat: add tournament bracket generation"`
5. Push and create PR (if using GitHub/GitLab)

### Commit message format:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `refactor:` - Code refactoring
- `test:` - Tests

### Example commits:
```bash
git commit -m "feat: add Dockerfile and docker-compose.yml for containerization"
git commit -m "feat: implement tournament bracket tree generation"
git commit -m "feat: add tournament creation UI form"
git commit -m "feat: add Kubernetes deployment manifests"
git commit -m "docs: add C4 architecture diagrams"
```

---

## 🎯 Priority Order (Updated for Microservices)

### СРОЧНО (делай первым):
1. **Создать Tournament Service** - отдельный микросервис
   - Создать папку `tournament-service/`
   - Перенести tournament код
   - Настроить отдельный порт (8002)
   - Протестировать работу

2. **Docker для Tournament Service** - контейнеризация сервиса

3. **Kubernetes для Tournament Service** - деплой с репликами

4. **Service Communication** - общение с другими сервисами (auth, notifications)

5. **Documentation** - C4 диаграммы с микросервисной архитектурой

**👉 Подробная инструкция в `DANIAL_TASKS_MICROSERVICES.md`**

---

## 💡 Quick Start Commands

### Test Backend API:
```bash
# Start backend
uvicorn main:app --reload

# Test tournament creation
curl -X POST "http://localhost:8000/tournaments/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Tournament", "start_date": "2024-01-15T10:00:00", "max_participants": 8}'

# List tournaments (after you implement GET endpoint)
curl http://localhost:8000/tournaments
```

### Test Frontend:
```bash
cd frontend
npm run dev
# Open http://localhost:3000/tournaments
```

### Check what Yazan has:
```bash
# Check user registration (Yazan's work)
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@test.com", "password": "test123", "full_name": "Admin User", "role": "admin"}'
```

---

## 🔗 Integration Points with Other Team Members

### With Yazan (Auth/Security):
- **Current:** Tournament endpoints work without auth
- **Future:** When JWT/RBAC is ready, add auth to admin endpoints
- **Tournament registration:** Will need to link to user IDs from auth system

### With Yeldana (Frontend/UI):
- Frontend structure already set up by Yeldana
- Use existing design system (`index.css`)
- Follow UX guidelines (max 2 clicks rule)

### With Shattyk (Notifications):
- When matches start, could trigger notifications (Shattyk's module)
- Tournament completion could send notifications


