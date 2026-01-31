#!/bin/bash
# Complete cleanup and restart script for GYM IT System microservices
# This script stops all containers, removes volumes, and rebuilds/restarts everything

set -e

echo "============================================"
echo "GYM IT System - Complete Cleanup & Restart"
echo "============================================"
echo ""
echo "This will:"
echo "  1. Stop all Docker containers"
echo "  2. Remove all Docker volumes (databases will be reset)"
echo "  3. Remove Docker images (forces rebuild)"
echo "  4. Rebuild all services"
echo "  5. Start all services"
echo ""
read -p "Are you sure you want to continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

echo ""
echo "Step 1: Stopping all containers..."
docker compose -f docker-compose.microservices.yml down -v 2>/dev/null || true
docker compose -f docker-compose.yml down -v 2>/dev/null || true

echo ""
echo "Step 2: Removing GYM IT containers..."
docker ps -a --format '{{.Names}}' | grep "gymit-" | xargs -r docker rm -f 2>/dev/null || true

echo ""
echo "Step 3: Removing GYM IT images..."
docker images --format '{{.Repository}}:{{.Tag}}' | grep "gymit-" | xargs -r docker rmi -f 2>/dev/null || true
docker images --format '{{.Repository}}:{{.Tag}}' | grep "gym-it-system" | xargs -r docker rmi -f 2>/dev/null || true

echo ""
echo "Step 4: Removing GYM IT volumes..."
docker volume ls --format '{{.Name}}' | grep "gym" | xargs -r docker volume rm 2>/dev/null || true

echo ""
echo "Step 5: Removing GYM IT networks..."
docker network ls --format '{{.Name}}' | grep "microservices-net" | xargs -r docker network rm 2>/dev/null || true

echo ""
echo "Step 6: Pruning Docker system..."
docker system prune -f

echo ""
echo "✓ Cleanup complete!"
echo ""
echo "Step 7: Rebuilding and starting services..."
docker compose -f docker-compose.microservices.yml up --build -d

echo ""
echo "Waiting for services to be ready..."
sleep 10

echo ""
echo "Step 8: Checking service status..."
docker compose -f docker-compose.microservices.yml ps

echo ""
echo "============================================"
echo "✓ All services restarted successfully!"
echo "============================================"
echo ""
echo "Access the application at: http://localhost:8000"
echo "Admin login: admin@gym.com / admin"
echo ""
echo "To view logs:"
echo "  docker compose -f docker-compose.microservices.yml logs -f"
echo ""
echo "To view specific service logs:"
echo "  docker compose -f docker-compose.microservices.yml logs -f user-service"
echo ""
