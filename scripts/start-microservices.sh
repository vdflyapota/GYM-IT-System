#!/bin/bash
# Quick start script for microservices

set -e

echo "====================================="
echo "GYM IT Microservices Quick Start"
echo "====================================="

# Check if docker is available
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed"
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.microservices.example .env
    echo "✓ .env file created"
fi

echo ""
echo "Checking for conflicting containers..."
echo ""

# Stop old monolithic containers if they're running
if docker ps -a --format '{{.Names}}' | grep -q "gymit-api\|gymit-db"; then
    echo "Found old monolithic containers. Stopping them..."
    docker compose -f docker-compose.yml down 2>/dev/null || true
    echo "✓ Old containers stopped"
fi

# Check if required ports are available
echo ""
echo "Checking port availability..."
echo ""

ports_in_use=false
required_ports=(8000 8001 8002 8003 8004)

for port in "${required_ports[@]}"; do
    if command -v lsof &> /dev/null; then
        # Use lsof if available (Linux/Mac)
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            echo "⚠ Port $port is in use"
            process_info=$(lsof -Pi :$port -sTCP:LISTEN 2>/dev/null | tail -n 1)
            echo "  Process: $process_info"
            ports_in_use=true
        fi
    elif command -v netstat &> /dev/null; then
        # Fallback to netstat (Windows/Linux)
        if netstat -tuln 2>/dev/null | grep -q ":$port "; then
            echo "⚠ Port $port is in use"
            ports_in_use=true
        fi
    elif command -v ss &> /dev/null; then
        # Another fallback to ss (modern Linux)
        if ss -tuln 2>/dev/null | grep -q ":$port "; then
            echo "⚠ Port $port is in use"
            ports_in_use=true
        fi
    fi
done

if [ "$ports_in_use" = true ]; then
    echo ""
    echo "❌ ERROR: Required ports are already in use!"
    echo ""
    echo "To fix this, you can:"
    echo "1. Stop all Docker containers:"
    echo "   docker stop \$(docker ps -aq)"
    echo ""
    echo "2. Find and kill the process using the port (example for port 8000):"
    echo "   # On Linux/Mac:"
    echo "   lsof -ti:8000 | xargs kill -9"
    echo ""
    echo "   # Or manually find the process:"
    echo "   lsof -i :8000"
    echo "   # Then kill it:"
    echo "   kill -9 <PID>"
    echo ""
    echo "3. Or use the stop script first:"
    echo "   ./scripts/stop-microservices.sh"
    echo ""
    exit 1
fi

echo "✓ All required ports are available"

echo ""
echo "Starting all microservices..."
echo ""

# Start services with --remove-orphans to clean up any orphan containers
docker compose -f docker-compose.microservices.yml up -d --remove-orphans

echo ""
echo "Waiting for services to be healthy..."
sleep 10

# Check service health
echo ""
echo "Checking service health..."
echo ""

services=("api-gateway:8000" "auth-service:8001" "user-service:8002" "tournament-service:8003" "notification-service:8004")

for service in "${services[@]}"; do
    IFS=':' read -r name port <<< "$service"
    if curl -f http://localhost:$port/healthz &>/dev/null; then
        echo "✓ $name is healthy"
    else
        echo "✗ $name is not responding"
    fi
done

echo ""
echo "====================================="
echo "Services are running!"
echo "====================================="
echo ""
echo "Access points:"
echo "  API Gateway:         http://localhost:8000"
echo "  Auth Service:        http://localhost:8001"
echo "  User Service:        http://localhost:8002"
echo "  Tournament Service:  http://localhost:8003"
echo "  Notification Service: http://localhost:8004"
echo ""
echo "Databases:"
echo "  Auth DB:        localhost:5433"
echo "  User DB:        localhost:5434"
echo "  Tournament DB:  localhost:5435"
echo "  Redis:          localhost:6379"
echo ""
echo "To view logs:"
echo "  docker compose -f docker-compose.microservices.yml logs -f [service-name]"
echo ""
echo "To stop all services:"
echo "  docker compose -f docker-compose.microservices.yml down"
echo ""
