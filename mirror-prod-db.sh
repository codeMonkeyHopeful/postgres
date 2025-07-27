#!/bin/bash
set -e
PROD_SERVER="neo@192.168.0.209"
PROD_CONTAINER="postgres_api"
PROD_COMPOSE_DIR="/home/neo/repos/postgres"
BACKUP_DIR="/home/neo/tmp"
DATABASE_NAME="api_db"
DATABASE_USER="neo"

SSH_CONTROL_PATH="/tmp/ssh-control-%r@%h:%p"
SSH_OPTS="-o ControlMaster=auto -o ControlPath=$SSH_CONTROL_PATH -o ControlPersist=10m"

echo "Establishing SSH connection..."
ssh $SSH_OPTS $PROD_SERVER "echo 'SSH connection established'"

echo "Creating backup directory..."
ssh $SSH_OPTS $PROD_SERVER "mkdir -p $BACKUP_DIR"

echo "Creating database dump from production..."
ssh $SSH_OPTS $PROD_SERVER "
    docker exec $PROD_CONTAINER pg_dump -U $DATABASE_USER -d $DATABASE_NAME --clean --if-exists > $BACKUP_DIR/database-dump.sql
    chown \$(id -u):\$(id -g) $BACKUP_DIR/database-dump.sql
    echo 'Dump created, size:'
    ls -lh $BACKUP_DIR/database-dump.sql
"

echo "Transferring database dump..."
scp $SSH_OPTS $PROD_SERVER:$BACKUP_DIR/database-dump.sql /tmp/

echo "Stopping local services..."
docker compose -f /home/neo/repos/postgres/docker-compose.yml down

echo "Starting local services..."
docker compose -f /home/neo/repos/postgres/docker-compose.yml up -d

echo "Waiting for local database to be ready..."
sleep 15

echo "Creating database if it doesn't exist..."
docker exec postgres_api psql -U $DATABASE_USER -d postgres -c "CREATE DATABASE $DATABASE_NAME;" 2>/dev/null || echo "Database already exists or creation failed"

echo "Restoring database..."
docker exec -i postgres_api psql -U $DATABASE_USER -d $DATABASE_NAME < /tmp/database-dump.sql

echo "Verifying restore..."
echo "Tables in database:"
docker exec postgres_api psql -U $DATABASE_USER -d $DATABASE_NAME -c '\dt'

echo "Row count in users table:"
docker exec postgres_api psql -U $DATABASE_USER -d $DATABASE_NAME -c 'SELECT count(*) FROM users;' || echo "Users table not found"

# Cleanup
rm -f /tmp/database-dump.sql
ssh $SSH_OPTS $PROD_SERVER "rm -f $BACKUP_DIR/database-dump.sql"
ssh $SSH_OPTS -O exit $PROD_SERVER 2>/dev/null || true

echo "Database mirroring complete!"
