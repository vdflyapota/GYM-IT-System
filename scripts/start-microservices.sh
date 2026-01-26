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
echo "Starting all microservices..."
echo ""

# Start services
docker compose -f docker-compose.microservices.yml up -d

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
