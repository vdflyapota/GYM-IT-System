#!/bin/bash
# Diagnostic script to check port availability and Docker status

echo "====================================="
echo "GYM IT System - Diagnostic Check"
echo "====================================="
echo ""

# Check Docker
echo "1. Checking Docker..."
if command -v docker &> /dev/null; then
    echo "   ✓ Docker is installed"
    docker --version
    
    if docker ps >/dev/null 2>&1; then
        echo "   ✓ Docker daemon is running"
    else
        echo "   ✗ Docker daemon is not running"
        echo "   Please start Docker and try again"
        exit 1
    fi
else
    echo "   ✗ Docker is not installed"
    exit 1
fi

echo ""
echo "2. Checking Docker Compose..."
if docker compose version >/dev/null 2>&1; then
    echo "   ✓ Docker Compose is available"
    docker compose version
else
    echo "   ✗ Docker Compose is not available"
    exit 1
fi

echo ""
echo "3. Checking for running Docker containers..."
running_containers=$(docker ps --format '{{.Names}}' | grep "gymit-" || true)
if [ -n "$running_containers" ]; then
    echo "   ⚠ Found running GYM IT containers:"
    echo "$running_containers" | sed 's/^/     - /'
    echo ""
    echo "   Run './scripts/stop-microservices.sh' to stop them"
else
    echo "   ✓ No GYM IT containers currently running"
fi

echo ""
echo "4. Checking port availability..."
required_ports=(8000 8001 8002 8003 8004 5433 5434 5435 6379)
ports_ok=true

for port in "${required_ports[@]}"; do
    if command -v lsof &> /dev/null; then
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            echo "   ✗ Port $port is IN USE"
            process_info=$(lsof -Pi :$port -sTCP:LISTEN 2>/dev/null | tail -n +2)
            echo "     $process_info"
            ports_ok=false
        else
            echo "   ✓ Port $port is available"
        fi
    elif command -v netstat &> /dev/null; then
        if netstat -tuln 2>/dev/null | grep -q ":$port "; then
            echo "   ✗ Port $port is IN USE"
            ports_ok=false
        else
            echo "   ✓ Port $port is available"
        fi
    elif command -v ss &> /dev/null; then
        if ss -tuln 2>/dev/null | grep -q ":$port "; then
            echo "   ✗ Port $port is IN USE"
            ports_ok=false
        else
            echo "   ✓ Port $port is available"
        fi
    else
        echo "   ⚠ Cannot check port $port (no lsof/netstat/ss available)"
    fi
done

echo ""
echo "5. Checking Docker networks..."
if docker network ls | grep -q "microservices-net"; then
    echo "   ✓ microservices-net network exists"
else
    echo "   ✓ microservices-net network will be created on startup"
fi

echo ""
echo "====================================="
echo "Diagnostic Summary"
echo "====================================="

if [ "$ports_ok" = true ]; then
    echo "✓ All checks passed! You can start the microservices:"
    echo "  ./scripts/start-microservices.sh"
else
    echo "✗ Some ports are in use. Please resolve the conflicts:"
    echo ""
    echo "To stop all Docker containers:"
    echo "  docker stop \$(docker ps -aq)"
    echo ""
    echo "To kill a process using a specific port (e.g., 8000):"
    echo "  lsof -ti:8000 | xargs kill -9"
    echo ""
    echo "Or use the stop script:"
    echo "  ./scripts/stop-microservices.sh"
fi

echo ""
