#!/bin/bash
# Stop script for microservices

set -e

echo "====================================="
echo "Stopping GYM IT Microservices"
echo "====================================="
echo ""

# Stop microservices
echo "Stopping microservices..."
docker compose -f docker-compose.microservices.yml down

# Also stop old monolithic containers if they exist
echo ""
echo "Stopping old monolithic containers (if any)..."
docker compose -f docker-compose.yml down 2>/dev/null || true

echo ""
echo "✓ All services stopped"
echo ""
echo "To remove volumes as well, run:"
echo "  docker compose -f docker-compose.microservices.yml down -v"
echo ""
