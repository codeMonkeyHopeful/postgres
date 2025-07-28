#!/bin/bash

# Load environment variables
source .env

# Exit on ANY error
set -e

echo "Starting database mirroring process."
echo "Copying from"
echo "Server: $SERVER_CONNECTION"
echo "Container: $SERVER_CONTAINER_NAME"
echo "Database: $POSTGRES_DB"

SSH_CONTROL_PATH="/tmp/ssh-control-%r@%h:%p"
SSH_OPTS="-o ControlMaster=auto -o ControlPath=$SSH_CONTROL_PATH -o ControlPersist=10m"

echo "Establishing SSH connection..."
ssh $SSH_OPTS $SERVER_CONNECTION "echo 'SSH connection established'"

echo "Creating backup directory..."
ssh $SSH_OPTS $SERVER_CONNECTION "mkdir -p $BACKUP_DIR"

echo "Creating database dump from production..."
ssh $SSH_OPTS $SERVER_CONNECTION "
    docker exec $POSTGRES_CONTAINER_NAME pg_dump -U $POSTGRES_USER -d $POSTGRES_DB --clean --if-exists > $BACKUP_DIR/database-dump.sql
    chown \$(id -u):\$(id -g) $BACKUP_DIR/database-dump.sql
    echo 'Dump created, size:'
    ls -lh $BACKUP_DIR/database-dump.sql
"

echo "Transferring database dump..."
scp $SSH_OPTS $SERVER_CONNECTION:$BACKUP_DIR/database-dump.sql /tmp/

# Validate the dump was transferred
if [ ! -f /tmp/database-dump.sql ]; then
    echo "Failed to transfer database dump!"
    exit 1
fi

echo "Local dump size: $(ls -lh /tmp/database-dump.sql)"

echo "Stopping local services..."
docker compose -f /home/neo/repos/$POSTGRES_CONTAINER_NAME/docker-compose.yml down

echo "Removing old database volume for clean initialization..."
docker volume rm postgres_postgres_data 2>/dev/null || echo "Volume didn't exist or already removed"

echo "Starting local services..."
docker compose -f /home/neo/repos/$POSTGRES_CONTAINER_NAME/docker-compose.yml up -d

echo "Waiting for local database to be ready trying in $DB_STARTUP_WAIT seconds..."
sleep $DB_STARTUP_WAIT

echo "Waiting for PostgreSQL to be ready..."
for i in {1..20}; do
    if docker exec $POSTGRES_CONTAINER_NAME pg_isready -U $POSTGRES_USER >/dev/null 2>&1; then
        echo "PostgreSQL service ready after $i attempts"
        break
    fi
    echo "Attempt $i: Waiting for PostgreSQL service..."
    sleep 2
done

echo "Testing database connection with user $POSTGRES_USER..."
# Wait for the user and database to be ready
for i in {1..10}; do
    if docker exec $POSTGRES_CONTAINER_NAME psql -U $POSTGRES_USER -d $POSTGRES_DB -c "SELECT 1;" >/dev/null 2>&1; then
        echo "Database connection successful!"
        break
    fi
    echo "Attempt $i: Waiting for database initialization..."
    sleep 3
done

echo "Recreating database..."
docker exec $POSTGRES_CONTAINER_NAME psql -U $POSTGRES_USER -d postgres -c "DROP DATABASE IF EXISTS $POSTGRES_DB;"
docker exec $POSTGRES_CONTAINER_NAME psql -U $POSTGRES_USER -d postgres -c "CREATE DATABASE $POSTGRES_DB;"

echo "Restoring database..."
if docker exec -i $POSTGRES_CONTAINER_NAME psql -U $POSTGRES_USER -d $POSTGRES_DB < /tmp/database-dump.sql; then
    echo "Database restore successful"
else
    echo "Database restore failed!"
    exit 1
fi

echo "Verifying restore..."
echo "Tables in database:"
docker exec $POSTGRES_CONTAINER_NAME psql -U $POSTGRES_USER -d $POSTGRES_DB -c '\dt'

echo "Row count in users table:"
docker exec $POSTGRES_CONTAINER_NAME psql -U $POSTGRES_USER -d $POSTGRES_DB -c 'SELECT count(*) FROM users;' || echo "Users table not found"

# Cleanup
echo "Cleaning up temporary files..."
rm -f /tmp/database-dump.sql
ssh $SSH_OPTS $SERVER_CONNECTION "rm -f $BACKUP_DIR/database-dump.sql"
ssh $SSH_OPTS -O exit $SERVER_CONNECTION 2>/dev/null || true

echo "Database mirroring complete!"
