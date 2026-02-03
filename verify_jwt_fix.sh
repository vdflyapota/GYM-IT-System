#!/bin/bash

# Script to verify JWT configuration is correct in both services

echo "=========================================="
echo "JWT Configuration Verification"
echo "=========================================="
echo ""

# Check auth-service config
echo "Checking auth-service config..."
if grep -q "JWT_ALGORITHM" services/auth-service/src/config.py; then
    echo "✅ auth-service has JWT_ALGORITHM configured"
else
    echo "❌ auth-service is MISSING JWT_ALGORITHM"
fi

if grep -q "JWT_SECRET_KEY" services/auth-service/src/config.py; then
    echo "✅ auth-service has JWT_SECRET_KEY configured"
else
    echo "❌ auth-service is MISSING JWT_SECRET_KEY"
fi

echo ""

# Check tournament-service config
echo "Checking tournament-service config..."
if grep -q "JWT_ALGORITHM" services/tournament-service/src/config.py; then
    echo "✅ tournament-service has JWT_ALGORITHM configured"
else
    echo "❌ tournament-service is MISSING JWT_ALGORITHM"
fi

if grep -q "JWT_SECRET_KEY" services/tournament-service/src/config.py; then
    echo "✅ tournament-service has JWT_SECRET_KEY configured"
else
    echo "❌ tournament-service is MISSING JWT_SECRET_KEY"
fi

echo ""
echo "=========================================="
echo "Next Steps:"
echo "=========================================="
echo ""
echo "If all checks show ✅, the code is fixed!"
echo ""
echo "Now you MUST:"
echo "1. Restart services:"
echo "   docker compose restart auth-service tournament-service"
echo ""
echo "2. Log out and log back in to get fresh token"
echo ""
echo "3. Access leaderboard - should work!"
echo ""
echo "See QUICK_FIX.md for detailed instructions."
echo ""
