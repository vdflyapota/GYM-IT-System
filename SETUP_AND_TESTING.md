# GYM-IT-System Complete Setup & Testing Guide

## ✅ Project Status
- **Frontend**: 100% Complete - 11 pages with full API integration
- **Backend**: 5 microservices fully configured
- **Database**: PostgreSQL + Redis configured
- **Docker**: Multi-container setup ready
- **API**: All endpoints documented and integrated

---

## 🚀 Quick Start (Local Development)

### Prerequisites
- Node.js 16+
- Python 3.8+
- PostgreSQL 12+
- Redis 6+

### 1. Frontend Setup
```bash
cd frontend
npm install
npm run dev
# Frontend runs on http://localhost:5173
```

### 2. Backend Microservices Setup

#### Option A: Docker (Recommended)
```bash
docker-compose -f docker-compose.microservices.yml up
```

#### Option B: Local Python
```bash
# Terminal 1 - API Gateway (Port 8000)
python -m services.api_gateway.run

# Terminal 2 - Auth Service (Port 8001)
python -m services.auth_service.run

# Terminal 3 - User Service (Port 8002)
python -m services.user_service.run

# Terminal 4 - Tournament Service (Port 8003)
python -m services.tournament_service.run

# Terminal 5 - Notification Service (Port 8004)
python -m services.notification_service.run
```

---

## 🧪 Testing Checklist

### Frontend Pages (All Implemented)
- [x] **Home** (`/`) - Landing page with auth checks
- [x] **Login** (`/login`) - JWT authentication
- [x] **Register** (`/register`) - User registration with email
- [x] **Dashboard** (`/dashboard`) - User dashboard with stats
- [x] **Tournaments** (`/tournaments`) - List & join tournaments
- [x] **Leaderboard** (`/leaderboard`) - Ranked user list
- [x] **ClassSchedule** (`/class-schedule`) - Weekly class listings
- [x] **Hiring** (`/hiring`) - Job applications with CV upload
- [x] **Membership** (`/membership`) - Freeze/upgrade plans, class booking
- [x] **AdminReports** (`/admin/reports`) - User management
- [x] **KPIDashboard** (`/admin/kpi`) - MRR, churn, metrics
- [x] **Communications** (`/admin/communications`) - Bulk email/SMS
- [x] **AccessLogs** (`/admin/access-logs`) - Real-time access tracking

### API Integration Tests

#### 1. Authentication Flow
```bash
# Register new user
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!",
    "full_name": "Test User"
  }'

# Response should include access_token and user object

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!"
  }'
```

#### 2. User Data Retrieval
```bash
# Get current user (requires token)
curl -X GET http://localhost:8000/api/users/me \
  -H "Authorization: Bearer <your-token>"

# List all users (admin only)
curl -X GET http://localhost:8000/api/users/ \
  -H "Authorization: Bearer <admin-token>"
```

#### 3. Tournament Management
```bash
# List tournaments
curl -X GET http://localhost:8000/api/tournaments/ \
  -H "Authorization: Bearer <your-token>"

# Get leaderboard
curl -X GET http://localhost:8000/api/tournaments/leaderboard \
  -H "Authorization: Bearer <your-token>"

# Join tournament
curl -X POST http://localhost:8000/api/tournaments/{id}/join \
  -H "Authorization: Bearer <your-token>"
```

#### 4. Class Schedule
```bash
# Get class schedule
curl -X GET http://localhost:8000/api/classes/schedule \
  -H "Authorization: Bearer <your-token>"

# Register for class
curl -X POST http://localhost:8000/api/classes/{id}/register \
  -H "Authorization: Bearer <your-token>"
```

#### 5. Membership Management
```bash
# Get membership details
curl -X GET http://localhost:8000/api/membership/details \
  -H "Authorization: Bearer <your-token>"

# Freeze membership
curl -X POST http://localhost:8000/api/membership/freeze \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "reason": "vacation",
    "duration": "2"
  }'
```

#### 6. Admin Communications
```bash
# Send bulk email
curl -X POST http://localhost:8000/api/communications/email/bulk \
  -H "Authorization: Bearer <admin-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "recipients": ["user1@example.com", "user2@example.com"],
    "subject": "Gym Maintenance",
    "message": "We will be closed on..."
  }'
```

#### 7. Admin Analytics
```bash
# Get KPI data
curl -X GET http://localhost:8000/api/analytics/kpi \
  -H "Authorization: Bearer <admin-token>"

# Get access logs
curl -X GET http://localhost:8000/api/analytics/access-logs?limit=50 \
  -H "Authorization: Bearer <admin-token>"
```

---

## 📊 Manual Testing Steps

### Step 1: Test User Registration
1. Open http://localhost:5173/register
2. Enter details:
   - Name: John Doe
   - Email: john@example.com
   - Password: Test123!
3. Click Register
4. Should redirect to login with message

### Step 2: Test User Login
1. Open http://localhost:5173/login
2. Enter credentials:
   - Email: john@example.com
   - Password: Test123!
3. Click Login
4. Should redirect to /dashboard

### Step 3: Test Membership Management
1. Logged in, click "Membership" in sidebar
2. View current membership plan
3. Try to upgrade plan
4. Try to freeze membership
5. Book a class
6. View my bookings

### Step 4: Test Tournaments
1. Click "Tournaments" in sidebar
2. See list of active tournaments
3. Click "Join Tournament" button
4. Check leaderboard to see updated rankings

### Step 5: Test Admin Features (Login as Admin)
1. Create admin account:
```bash
curl -X POST http://localhost:8000/api/auth/create_admin \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "Admin123!",
    "full_name": "Admin User"
  }'
```
2. Login as admin
3. Check Admin menu options:
   - User Reports - See all users
   - KPI Dashboard - View metrics
   - Communications - Send bulk messages
   - Access Logs - See real-time access

### Step 6: Test Class Booking
1. Click "Class Schedule" in sidebar
2. View available classes
3. Book a class
4. Go to Membership > My Bookings
5. See booked class
6. Cancel booking

### Step 7: Test Job Application
1. Click "Hiring" in sidebar
2. View job listings
3. Fill application form
4. Upload CV
5. Submit application

---

## 🔍 Troubleshooting

### Frontend Issues
```bash
# Clear cache and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Backend Issues
```bash
# Check service is running
curl http://localhost:8000/healthz
curl http://localhost:8001/healthz
curl http://localhost:8002/healthz
curl http://localhost:8003/healthz
curl http://localhost:8004/healthz

# Check logs
docker-compose -f docker-compose.microservices.yml logs -f api-gateway
docker-compose -f docker-compose.microservices.yml logs -f auth-service
```

### Database Issues
```bash
# Check PostgreSQL is running
psql -U postgres -h localhost

# Check Redis is running
redis-cli ping
# Should respond with PONG
```

### API Connection Issues
1. Check API base URL in `frontend/src/services/api.js`
2. Verify backend services are responding
3. Check CORS settings in backend config
4. Check JWT token is valid (not expired)
5. Verify Authorization header format: `Bearer <token>`

---

## 📋 Implementation Checklist

### Frontend Features
- [x] Authentication (Register, Login, Logout)
- [x] User Dashboard with stats
- [x] Tournament listing and joining
- [x] Leaderboard with rankings
- [x] Class schedule and booking
- [x] Job application with file upload
- [x] Membership management (freeze/upgrade)
- [x] Admin reports
- [x] KPI dashboard with metrics
- [x] Bulk communications (Email/SMS)
- [x] Real-time access logs
- [x] Role-based navigation (Admin, Trainer, User)
- [x] Error handling and loading states
- [x] Responsive design

### Backend Services
- [x] API Gateway - Request routing
- [x] Auth Service - Registration, login, token generation
- [x] User Service - Profile management, role assignment
- [x] Tournament Service - Tournament CRUD, leaderboard
- [x] Notification Service - Email/SMS notifications
- [x] Database models - All entities configured
- [x] JWT validation - Token-based auth
- [x] Error handling - Consistent error responses
- [x] CORS configuration - Frontend can communicate

### Database
- [x] PostgreSQL schema - All tables created
- [x] Migrations - Version controlled
- [x] Redis caching - Session/cache storage
- [x] Relationships - Foreign keys configured
- [x] Indexes - Performance optimized

### DevOps
- [x] Docker - All services containerized
- [x] docker-compose - Multi-container orchestration
- [x] Health checks - Service monitoring
- [x] Environment variables - Configuration management
- [x] Volumes - Data persistence

---

## 📈 Performance Notes

### Frontend Optimization
- Vite for fast development and production builds
- React.lazy() for code-splitting
- CSS variables for efficient styling
- Mock data fallback for offline testing

### Backend Optimization
- JWT caching with Redis
- Database connection pooling
- Service-to-service communication
- Request logging and monitoring

---

## 🔒 Security Checklist

- [x] JWT token-based authentication
- [x] Password hashing (bcrypt)
- [x] CORS configuration
- [x] XSS protection (React auto-escaping)
- [x] CSRF tokens (backend validation)
- [x] Input validation (frontend + backend)
- [x] Role-based access control (RBAC)
- [x] Secure headers (Content-Type, etc.)
- [x] Error handling (no sensitive info in responses)
- [x] Logging (request/response tracking)

---

## 📞 Support

For issues or questions:
1. Check error messages in browser console
2. Check backend logs in terminal
3. Verify API responses with curl
4. Check database connections
5. Verify environment variables

---

## 🎯 Summary

**GYM-IT-System is fully implemented and ready for:**
- Local development and testing
- Docker deployment
- Production deployment (with configuration)
- Integration testing with backend
- User acceptance testing
- Performance optimization
- Security hardening

All 13 frontend pages are connected to real backend APIs with fallback to mock data for development.
