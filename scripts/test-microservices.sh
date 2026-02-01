#!/bin/bash
# Test script for microservices

set -e

API_GATEWAY="http://localhost:8000"

echo "====================================="
echo "Testing Microservices"
echo "====================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

test_passed=0
test_failed=0

# Function to test endpoint
test_endpoint() {
    local name=$1
    local url=$2
    local method=${3:-GET}
    local data=${4:-}
    
    echo -n "Testing $name... "
    
    if [ -n "$data" ]; then
        response=$(curl -s -w "\n%{http_code}" -X $method -H "Content-Type: application/json" -d "$data" "$url")
    else
        response=$(curl -s -w "\n%{http_code}" -X $method "$url")
    fi
    
    http_code=$(echo "$response" | tail -n 1)
    body=$(echo "$response" | head -n -1)
    
    if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
        echo -e "${GREEN}✓ PASS${NC} (HTTP $http_code)"
        ((test_passed++))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC} (HTTP $http_code)"
        echo "Response: $body"
        ((test_failed++))
        return 1
    fi
}

# Test health endpoints
echo "1. Testing Health Endpoints"
echo "----------------------------"
test_endpoint "API Gateway Health" "$API_GATEWAY/healthz"
test_endpoint "Auth Service Health" "$API_GATEWAY/api/auth/health"
test_endpoint "User Service Health" "$API_GATEWAY/api/users/health"
test_endpoint "Tournament Service Health" "$API_GATEWAY/api/tournaments/health"
test_endpoint "Notification Service Health" "$API_GATEWAY/api/notifications/health"
echo ""

# Test authentication
echo "2. Testing Authentication"
echo "-------------------------"

# Register a new user
echo -n "Registering new user... "
register_response=$(curl -s -w "\n%{http_code}" -X POST \
    -H "Content-Type: application/json" \
    -d '{"email":"test@example.com","password":"testpass123","full_name":"Test User"}' \
    "$API_GATEWAY/api/auth/register")

register_code=$(echo "$register_response" | tail -n 1)
if [ "$register_code" -eq 201 ] || [ "$register_code" -eq 409 ]; then
    echo -e "${GREEN}✓ PASS${NC} (HTTP $register_code)"
    ((test_passed++))
else
    echo -e "${RED}✗ FAIL${NC} (HTTP $register_code)"
    ((test_failed++))
fi

# Try to login (will fail if not approved)
echo -n "Attempting login... "
login_response=$(curl -s -w "\n%{http_code}" -X POST \
    -H "Content-Type: application/json" \
    -d '{"email":"test@example.com","password":"testpass123"}' \
    "$API_GATEWAY/api/auth/login")

login_code=$(echo "$login_response" | tail -n 1)
if [ "$login_code" -eq 200 ] || [ "$login_code" -eq 403 ]; then
    echo -e "${GREEN}✓ PASS${NC} (HTTP $login_code - Expected, user needs approval)"
    ((test_passed++))
else
    echo -e "${RED}✗ FAIL${NC} (HTTP $login_code)"
    ((test_failed++))
fi

# Try admin login
echo -n "Testing admin login... "
admin_login_response=$(curl -s -w "\n%{http_code}" -X POST \
    -H "Content-Type: application/json" \
    -d '{"email":"admin@gym.it","password":"admin123"}' \
    "$API_GATEWAY/api/auth/login")

admin_login_code=$(echo "$admin_login_response" | tail -n 1)
admin_body=$(echo "$admin_login_response" | head -n -1)

if [ "$admin_login_code" -eq 200 ]; then
    echo -e "${GREEN}✓ PASS${NC} (HTTP $admin_login_code)"
    ((test_passed++))
    
    # Extract token
    TOKEN=$(echo "$admin_body" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
    echo "  Token obtained: ${TOKEN:0:20}..."
else
    echo -e "${RED}✗ FAIL${NC} (HTTP $admin_login_code)"
    echo "Response: $admin_body"
    ((test_failed++))
    TOKEN=""
fi
echo ""

# Test authenticated endpoints
if [ -n "$TOKEN" ]; then
    echo "3. Testing Authenticated Endpoints"
    echo "-----------------------------------"
    
    # Test user profile
    echo -n "Getting user profile... "
    profile_response=$(curl -s -w "\n%{http_code}" \
        -H "Authorization: Bearer $TOKEN" \
        "$API_GATEWAY/api/users/me")
    
    profile_code=$(echo "$profile_response" | tail -n 1)
    if [ "$profile_code" -eq 200 ]; then
        echo -e "${GREEN}✓ PASS${NC} (HTTP $profile_code)"
        ((test_passed++))
    else
        echo -e "${RED}✗ FAIL${NC} (HTTP $profile_code)"
        ((test_failed++))
    fi
    
    # Test list users
    echo -n "Listing users... "
    users_response=$(curl -s -w "\n%{http_code}" \
        -H "Authorization: Bearer $TOKEN" \
        "$API_GATEWAY/api/users/")
    
    users_code=$(echo "$users_response" | tail -n 1)
    if [ "$users_code" -eq 200 ]; then
        echo -e "${GREEN}✓ PASS${NC} (HTTP $users_code)"
        ((test_passed++))
    else
        echo -e "${RED}✗ FAIL${NC} (HTTP $users_code)"
        ((test_failed++))
    fi
    
    # Test create tournament
    echo -n "Creating tournament... "
    tournament_response=$(curl -s -w "\n%{http_code}" -X POST \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d '{"name":"Test Tournament","start_date":"2026-02-01T10:00:00Z","max_participants":8}' \
        "$API_GATEWAY/api/tournaments/")
    
    tournament_code=$(echo "$tournament_response" | tail -n 1)
    if [ "$tournament_code" -eq 201 ]; then
        echo -e "${GREEN}✓ PASS${NC} (HTTP $tournament_code)"
        ((test_passed++))
    else
        echo -e "${RED}✗ FAIL${NC} (HTTP $tournament_code)"
        ((test_failed++))
    fi
    
    # Test list tournaments
    echo -n "Listing tournaments... "
    tournaments_response=$(curl -s -w "\n%{http_code}" \
        -H "Authorization: Bearer $TOKEN" \
        "$API_GATEWAY/api/tournaments/")
    
    tournaments_code=$(echo "$tournaments_response" | tail -n 1)
    if [ "$tournaments_code" -eq 200 ]; then
        echo -e "${GREEN}✓ PASS${NC} (HTTP $tournaments_code)"
        ((test_passed++))
    else
        echo -e "${RED}✗ FAIL${NC} (HTTP $tournaments_code)"
        ((test_failed++))
    fi
    
    echo ""
fi

# Summary
echo "====================================="
echo "Test Summary"
echo "====================================="
echo -e "Passed: ${GREEN}$test_passed${NC}"
echo -e "Failed: ${RED}$test_failed${NC}"
echo ""

if [ $test_failed -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed.${NC}"
    exit 1
fi
