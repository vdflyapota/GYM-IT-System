#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "======================================"
echo "GYM-IT-System Full Integration Check"
echo "======================================"
echo ""

# Check Frontend
echo -e "${YELLOW}Checking Frontend...${NC}"
if [ -d "frontend/src" ]; then
    echo -e "${GREEN}✓ Frontend directory exists${NC}"
    
    # Check key pages exist
    pages=("Login" "Register" "Dashboard" "Tournaments" "Leaderboard" "ClassSchedule" "AdminReports" "MembershipPortal" "KPIDashboard" "Communications" "AccessLogs")
    
    for page in "${pages[@]}"; do
        if [ -f "frontend/src/pages/${page}.jsx" ]; then
            echo -e "${GREEN}✓ ${page}.jsx exists${NC}"
        else
            echo -e "${RED}✗ ${page}.jsx missing${NC}"
        fi
    done
    
    # Check API service exists
    if [ -f "frontend/src/services/api.js" ]; then
        echo -e "${GREEN}✓ API service layer exists${NC}"
    else
        echo -e "${RED}✗ API service layer missing${NC}"
    fi
else
    echo -e "${RED}✗ Frontend directory not found${NC}"
fi

echo ""

# Check Backend
echo -e "${YELLOW}Checking Backend Microservices...${NC}"
services=("api-gateway" "auth-service" "user-service" "tournament-service" "notification-service")

for service in "${services[@]}"; do
    if [ -d "services/${service}" ]; then
        if [ -f "services/${service}/src/app.py" ]; then
            echo -e "${GREEN}✓ ${service} exists with app.py${NC}"
        else
            echo -e "${RED}✗ ${service} missing app.py${NC}"
        fi
        
        if [ -f "services/${service}/requirements.txt" ]; then
            echo -e "${GREEN}✓ ${service} has requirements.txt${NC}"
        else
            echo -e "${RED}✗ ${service} missing requirements.txt${NC}"
        fi
    else
        echo -e "${RED}✗ ${service} directory not found${NC}"
    fi
done

echo ""

# Check Docker configuration
echo -e "${YELLOW}Checking Docker Configuration...${NC}"
if [ -f "docker-compose.yml" ]; then
    echo -e "${GREEN}✓ docker-compose.yml exists${NC}"
else
    echo -e "${RED}✗ docker-compose.yml missing${NC}"
fi

if [ -f "docker-compose.microservices.yml" ]; then
    echo -e "${GREEN}✓ docker-compose.microservices.yml exists${NC}"
else
    echo -e "${RED}✗ docker-compose.microservices.yml missing${NC}"
fi

echo ""

# Check Database configuration
echo -e "${YELLOW}Checking Database Configuration...${NC}"
if [ -d "k8s/databases" ]; then
    echo -e "${GREEN}✓ Database configs exist${NC}"
else
    echo -e "${RED}✗ Database configs missing${NC}"
fi

echo ""

# Summary
echo "======================================"
echo "GYM-IT-System Structure Check Complete"
echo "======================================"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Start microservices: docker-compose -f docker-compose.microservices.yml up"
echo "2. Start frontend: cd frontend && npm run dev"
echo "3. Test registration at http://localhost:5173/register"
echo "4. Test login at http://localhost:5173/login"
echo "5. Access dashboard at http://localhost:5173/dashboard"
echo ""
