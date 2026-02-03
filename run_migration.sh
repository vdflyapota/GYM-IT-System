#!/bin/bash
# Easy migration runner for adding is_active column
# Run this from the project root directory

echo "========================================="
echo "Database Migration: Add is_active Column"
echo "========================================="
echo ""

# Check if docker-compose is running
if ! docker-compose ps | grep -q "user-service"; then
    echo "❌ Error: user-service container is not running"
    echo "Please start services with: docker-compose up -d"
    exit 1
fi

# Find the database container name
DB_CONTAINER=$(docker-compose ps -q user-service-db || docker-compose ps -q postgres)

if [ -z "$DB_CONTAINER" ]; then
    echo "❌ Error: Could not find database container"
    echo "Looking for containers..."
    docker-compose ps
    exit 1
fi

echo "✓ Found database container"
echo ""
echo "Running migration..."
echo ""

# Run the SQL migration
docker exec -i $DB_CONTAINER psql -U postgres -d user_service < services/user-service/migrations/add_is_active_column.sql

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Migration completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Restart the user-service:"
    echo "   docker-compose restart user-service"
    echo ""
    echo "2. Test the profile page - it should now load correctly"
else
    echo ""
    echo "❌ Migration failed"
    echo ""
    echo "Alternative: Run Python migration script:"
    echo "   cd services/user-service"
    echo "   python migrate_db.py"
fi
