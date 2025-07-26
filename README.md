# PostgreSQL API

A Docker-based PostgreSQL database setup with pgAdmin web interface for quickly standing up a PostgreSQL database for any project. Perfect for API backends, development environments, and rapid prototyping.

## Overview

This project provides a containerized PostgreSQL database with pgAdmin web interface, designed for quickly standing up a PostgreSQL database for any project. Whether you need an API backend, development environment, or database for prototyping, this setup gets you running in minutes with minimal configuration.

## Features

- 🐳 **Docker Compose Setup** - Easy one-command deployment
- 🗄️ **PostgreSQL 15** - Latest stable PostgreSQL database
- 🌐 **pgAdmin Web Interface** - Browser-based database management
- 💾 **Persistent Storage** - Data volumes for database and pgAdmin persistence
- 🔍 **Health Monitoring** - Built-in health checks for database availability
- 🔒 **Configurable Security** - Environment-based user and password management
- 🌐 **Network Isolation** - Dedicated Docker network for service communication
- 📋 **TODO:** Interactive Python CLI script for automated setup and configuration

## Prerequisites

- Docker
- Docker Compose
- Git

## Quick Start

1. **Clone the repository:**

```bash
git clone https://github.com/codeMonkeyHopeful/postgres-api.git
cd postgres-api
```

2. **Configure environment variables:**

```bash
cp .env.example .env
# Edit .env with your preferred settings
```

3. **Create the external network (NOTE: The network (pgnet) can be named whatever you want, but needs to follow the same steps below with that chosen name AND update the docker-compose.yml file as needed):**

```bash
docker network create pgnet
```

4. **Start the services:**

```bash
docker compose up -d
```

_Note: Docker volumes (`postgres_data` and `pgadmin_data`) will be automatically created on first run._

5. **Access pgAdmin:**
   - Open your browser to `http://localhost:{PGADMIN_PORT}`
   - Login with the email and password from your `.env` file

## Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

```bash
# PostgreSQL Configuration
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=your_database_name
POSTGRES_CONTAINER_NAME=postgres_api
POSTGRES_PORT=5432

# pgAdmin Configuration
PGADMIN_DEFAULT_EMAIL=admin@example.com
PGADMIN_DEFAULT_PASSWORD=your_pgadmin_password
PGADMIN_PORT=8080
```

### Variable Descriptions

| Variable                   | Description                          | Example             |
| -------------------------- | ------------------------------------ | ------------------- |
| `POSTGRES_USER`            | Database user for connections        | `dbuser`            |
| `POSTGRES_PASSWORD`        | Password for database user           | `securepassword123` |
| `POSTGRES_DB`              | Main database instance name          | `myapp_db`          |
| `POSTGRES_CONTAINER_NAME`  | Container name for PostgreSQL        | `postgres_api`      |
| `POSTGRES_PORT`            | Port for PostgreSQL (standard: 5432) | `5432`              |
| `PGADMIN_DEFAULT_EMAIL`    | Email to login to pgAdmin            | `admin@company.com` |
| `PGADMIN_DEFAULT_PASSWORD` | Password for pgAdmin interface       | `adminpassword`     |
| `PGADMIN_PORT`             | Port for pgAdmin web interface       | `8080`              |

## Services

### PostgreSQL Database

- **Image:** `postgres:15`
- **Container:** `postgres_api`
- **Port:** `5432` (configurable)
- **Features:**
  - Automatic restart unless stopped
  - Health check monitoring
  - Persistent data storage
  - Environment-based configuration

### pgAdmin Web Interface

- **Image:** `dpage/pgadmin4`
- **Container:** `pgadmin`
- **Port:** Configurable via `PGADMIN_PORT`
- **Features:**
  - Web-based database management
  - Automatic PostgreSQL connection setup
  - Persistent configuration storage
  - Depends on PostgreSQL health check

## Usage

### Connecting to PostgreSQL

**From your application:**

```bash
# Connection string format
postgresql://[POSTGRES_USER]:[POSTGRES_PASSWORD]@localhost:[POSTGRES_PORT]/[POSTGRES_DB]

# Example
postgresql://dbuser:securepassword123@localhost:5432/myapp_db
```

**Using psql command line:**

```bash
# Connect directly via Docker
docker exec -it postgres_api psql -U [POSTGRES_USER] -d [POSTGRES_DB]

# Connect from host machine (if psql is installed)
psql -h localhost -p [POSTGRES_PORT] -U [POSTGRES_USER] -d [POSTGRES_DB]
```

### Using pgAdmin

_Note: You may need to forward your port to the local machine if you are running the container on a remote server._
_Example forwarding syntax_

```bash
ssh -L [local_port]:localhost:[remote_port] [user]@[server]
```

1. **Access the interface:**

   - Navigate to `http://localhost:[PGADMIN_PORT]`
   - Login with your `PGADMIN_DEFAULT_EMAIL` and `PGADMIN_DEFAULT_PASSWORD`

2. **Add PostgreSQL server:**
   - Right-click "Servers" → "Create" → "Server"
   - **General tab:** Name: `PostgreSQL API`
   - **Connection tab:**
     - Host: `postgres` (container name)
     - Port: `5432`
     - Username: Your `POSTGRES_USER`
     - Password: Your `POSTGRES_PASSWORD`

## Management Commands

### Start services:

```bash
docker compose up -d
```

### Stop services:

```bash
docker compose down
```

### View logs:

```bash
# All services
docker compose logs

# PostgreSQL only
docker compose logs postgres

# pgAdmin only
docker compose logs pgadmin
```

### Check service status:

```bash
docker compose ps
```

### Restart services:

```bash
docker compose restart
```

## Data Persistence

The setup includes persistent volumes for:

- **postgres_data:** PostgreSQL database files
- **pgadmin_data:** pgAdmin configuration and settings

Data persists across container restarts and updates.

## Health Monitoring

PostgreSQL includes a health check that:

- Tests database connectivity every 10 seconds
- Has a 5-second timeout
- Retries up to 5 times before marking as unhealthy
- pgAdmin waits for PostgreSQL to be healthy before starting

## Backup and Restore

### Create Backup

```bash
# Create SQL dump
docker exec postgres_api pg_dump -U [POSTGRES_USER] [POSTGRES_DB] > backup.sql

# Create compressed backup
docker exec postgres_api pg_dump -U [POSTGRES_USER] [POSTGRES_DB] | gzip > backup.sql.gz
```

### Restore Backup

```bash
# Restore from SQL dump
docker exec -i postgres_api psql -U [POSTGRES_USER] [POSTGRES_DB] < backup.sql

# Restore from compressed backup
gunzip -c backup.sql.gz | docker exec -i postgres_api psql -U [POSTGRES_USER] [POSTGRES_DB]
```

## Network Configuration

The setup uses an external Docker network named `pgnet`:

```bash
# Create the network (required before first run)
docker network create pgnet

# View network details
docker network inspect pgnet
```

This allows for easy integration with other Docker services that need database access.

## Troubleshooting

### Common Issues

**Network doesn't exist:**

```bash
docker network create pgnet
```

**Permission denied errors:**

```bash
# Check container logs
docker compose logs postgres

# Verify environment variables
docker compose config
```

**Can't connect to database:**

```bash
# Check if container is running
docker compose ps

# Test database connectivity
docker exec postgres_api pg_isready -U [POSTGRES_USER] -d [POSTGRES_DB]
```

**pgAdmin connection issues:**

```bash
# Ensure PostgreSQL is healthy
docker compose ps

# Check pgAdmin logs
docker compose logs pgadmin
```

### Port Conflicts

If you encounter port conflicts, update the `.env` file:

- Change `POSTGRES_PORT` for database access
- Change `PGADMIN_PORT` for web interface access

## Security Considerations

- Use strong passwords for both PostgreSQL and pgAdmin
- Consider changing default ports in production
- Restrict network access as needed
- Regularly update container images
- Use environment variables for sensitive data (never commit passwords to git)

## Development Integration

This setup is ideal for:

- Quickly standing up PostgreSQL for any project
- Local development environments
- API backend development
- Database prototyping
- Learning PostgreSQL
- Testing database schemas
- Microservices requiring database backends

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test the Docker setup
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Note:** Always use strong passwords and secure your environment variables in production deployments.
