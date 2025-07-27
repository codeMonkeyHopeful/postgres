#!/bin/bash
# mirror-prod-db.sh

set -e

PROD_SERVER="neo@192.168.0.209"
PROD_CONTAINER="postgres_api"
LOCAL_VOLUME="postgres_data"
LOCAL_CONTAINER="postgres_api"
BACKUP_DIR="/home/neo/tmp"

# Set up SSH connection sharing
SSH_CONTROL_PATH="/tmp/ssh-control-%r@%h:%p"
SSH_OPTS="-o ControlMaster=auto -o ControlPath=$SSH_CONTROL_PATH -o ControlPersist=10m"

echo "Establishing SSH connection (enter password once)..."
ssh $SSH_OPTS $PROD_SERVER "echo 'SSH connection established'"

echo "Stopping local container..."
docker stop $LOCAL_CONTAINER 2>/dev/null || true
docker rm $LOCAL_CONTAINER 2>/dev/null || true

echo "Creating backup directory on remote server..."
ssh $SSH_OPTS $PROD_SERVER "mkdir -p $BACKUP_DIR"

echo "Syncing production data..."
ssh $SSH_OPTS $PROD_SERVER "
    docker run --rm \
        --volumes-from $PROD_CONTAINER \
        -v $BACKUP_DIR:/backup \
        alpine sh -c 'tar czf /backup/postgres-backup.tar.gz -C /var/lib/postgresql/data . && chown \$(id -u):\$(id -g) /backup/postgres-backup.tar.gz'
"

echo "Transferring backup..."
scp $SSH_OPTS $PROD_SERVER:$BACKUP_DIR/postgres-backup.tar.gz /tmp/

echo "Cleaning up remote backup..."
ssh $SSH_OPTS $PROD_SERVER "rm -f $BACKUP_DIR/postgres-backup.tar.gz"

echo "Closing SSH connection..."
ssh $SSH_OPTS -O exit $PROD_SERVER 2>/dev/null || true

echo "Restoring to local volume..."
docker volume rm $LOCAL_VOLUME 2>/dev/null || true
docker volume create $LOCAL_VOLUME

docker run --rm \
    -v $LOCAL_VOLUME:/data \
    -v /tmp:/backup \
    alpine tar xzf /backup/postgres-backup.tar.gz -C /data

rm -f /tmp/postgres-backup.tar.gz

echo "Starting local container..."
docker run --name $LOCAL_CONTAINER \
    -v $LOCAL_VOLUME:/var/lib/postgresql/data \
    -p 5432:5432 \
    -e POSTGRES_PASSWORD=yourpassword \
    -d postgres

echo "Database mirrored successfully!"
