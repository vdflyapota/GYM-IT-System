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

# Additional cleanup - stop any remaining gymit containers
echo ""
echo "Checking for any remaining GYM IT containers..."
remaining=$(docker ps -a --format '{{.Names}}' | grep "gymit-" || true)
if [ -n "$remaining" ]; then
    echo "Found remaining containers:"
    echo "$remaining"
    echo ""
    read -p "Do you want to stop them? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "$remaining" | xargs -r docker stop
        echo "$remaining" | xargs -r docker rm
        echo "✓ Remaining containers stopped and removed"
    fi
else
    echo "✓ No remaining containers found"
fi

echo ""
echo "✓ All services stopped"
echo ""
echo "To remove volumes as well, run:"
echo "  docker compose -f docker-compose.microservices.yml down -v"
echo ""
echo "To see all Docker containers:"
echo "  docker ps -a"
echo ""
