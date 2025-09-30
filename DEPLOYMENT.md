# HackSeek Deployment Guide

This guide covers the deployment of the HackSeek application to production environments.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Docker Deployment](#docker-deployment)
4. [Kubernetes Deployment](#kubernetes-deployment)
5. [Database Setup](#database-setup)
6. [Monitoring](#monitoring)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Software

- Docker & Docker Compose
- kubectl (for Kubernetes deployment)
- PostgreSQL client tools (psql, pg_dump, pg_restore)
- Git
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### Required Services

- Container registry (e.g., GitHub Container Registry, Docker Hub)
- Domain name and SSL certificates
- Database hosting (PostgreSQL 15+)
- Redis hosting
- External API keys (OpenAI, etc.)

## Environment Setup

### 1. Clone Repository

```bash
git clone https://github.com/your-username/hackseek.git
cd hackseek
```

### 2. Configure Environment Variables

Copy the production environment template:

```bash
cp .env.production .env.production.local
```

Update the following critical variables in `.env.production.local`:

```bash
# Database
DATABASE_PASSWORD=your_strong_database_password
DATABASE_URL=postgresql+asyncpg://hackseek_user:your_password@db_host:5432/hackseek_prod

# Security (generate strong random strings)
SECRET_KEY=your_very_long_random_secret_key
JWT_SECRET_KEY=your_jwt_secret_key

# API Keys
OPENAI_API_KEY=your_openai_api_key

# Monitoring
SENTRY_DSN=your_sentry_dsn

# Redis
REDIS_PASSWORD=your_redis_password

# Domains
API_BASE_URL=https://api.hackseek.app
FRONTEND_URL=https://hackseek.app
```

### 3. Generate SSL Certificates

For production, obtain SSL certificates from Let's Encrypt or your certificate provider:

```bash
# Create SSL directory
mkdir -p nginx/ssl

# Copy your certificates
cp your_certificate.pem nginx/ssl/cert.pem
cp your_private_key.pem nginx/ssl/key.pem
```

## Docker Deployment

### 1. Build Images

```bash
# Build backend image
docker build -t hackseek/backend:latest ./backend

# Build frontend image
docker build -t hackseek/frontend:latest ./frontend
```

### 2. Deploy with Docker Compose

```bash
# Start services
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

### 3. Initialize Database

```bash
# Run database migrations
docker-compose -f docker-compose.prod.yml exec backend python scripts/migrate_db.py upgrade

# Create initial data (optional)
docker-compose -f docker-compose.prod.yml exec backend python scripts/seed_db.py
```

## Kubernetes Deployment

### 1. Prepare Kubernetes Cluster

Ensure you have a Kubernetes cluster with:
- NGINX Ingress Controller
- cert-manager (for SSL certificates)
- Storage class for persistent volumes

### 2. Configure Secrets

Update `deploy/kubernetes/secret.yaml` with base64-encoded values:

```bash
# Encode secrets
echo -n "your_database_password" | base64
echo -n "your_secret_key" | base64

# Update secret.yaml with encoded values
```

### 3. Deploy Application

```bash
# Navigate to deployment directory
cd deploy

# Deploy everything
./deploy.sh deploy

# Check status
./deploy.sh status

# View logs
./deploy.sh logs backend
```

### 4. Configure DNS

Point your domain names to the ingress controller:

```
hackseek.app → [Ingress IP]
www.hackseek.app → [Ingress IP]
api.hackseek.app → [Ingress IP]
```

## Database Setup

### 1. Initialize Database

```bash
# Connect to database
psql -h your_db_host -U hackseek_user -d hackseek_prod

# Or using the migration script
python backend/scripts/migrate_db.py upgrade
```

### 2. Setup Backups

Configure automated backups:

```bash
# Install crontab for automated backups
crontab crontab.prod

# Test backup manually
python backend/scripts/backup_db.py backup

# List backups
python backend/scripts/backup_db.py list
```

### 3. Performance Tuning

Recommended PostgreSQL settings for production:

```sql
-- In postgresql.conf
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
```

## Monitoring

### 1. Health Checks

The application provides several health check endpoints:

- `GET /health` - Overall application health
- `GET /health/ready` - Readiness probe
- `GET /health/live` - Liveness probe

### 2. Application Metrics

Monitor key metrics:

- Response times
- Error rates
- Database connection pool
- Memory and CPU usage
- Active user sessions

### 3. Log Aggregation

Logs are structured and can be collected by:

- ELK Stack (Elasticsearch, Logstash, Kibana)
- Grafana + Loki
- Cloud logging services (CloudWatch, Stackdriver)

### 4. Error Tracking

Configure Sentry for error tracking:

```bash
# Set SENTRY_DSN in environment variables
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
```

## Troubleshooting

### Common Issues

#### Database Connection Errors

```bash
# Check database connectivity
python backend/scripts/migrate_db.py check-connection

# Check database logs
docker-compose logs postgres
kubectl logs deployment/postgres -n hackseek
```

#### Frontend Build Issues

```bash
# Clear Next.js cache
rm -rf frontend/.next

# Rebuild frontend
docker build --no-cache -t hackseek/frontend:latest ./frontend
```

#### SSL Certificate Issues

```bash
# Check certificate validity
openssl x509 -in nginx/ssl/cert.pem -text -noout

# Test SSL configuration
curl -vI https://hackseek.app
```

### Performance Issues

#### Slow Database Queries

```sql
-- Enable query logging
ALTER SYSTEM SET log_min_duration_statement = 1000;
SELECT pg_reload_conf();

-- Check slow queries
SELECT query, mean_time, calls
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

#### High Memory Usage

```bash
# Check container memory usage
docker stats

# Check Kubernetes resource usage
kubectl top pods -n hackseek
```

### Rollback Procedures

#### Docker Deployment

```bash
# Stop current deployment
docker-compose -f docker-compose.prod.yml down

# Deploy previous version
docker-compose -f docker-compose.prod.yml up -d
```

#### Kubernetes Deployment

```bash
# Rollback to previous revision
./deploy.sh rollback backend
./deploy.sh rollback frontend

# Rollback to specific revision
kubectl rollout undo deployment/backend --to-revision=2 -n hackseek
```

### Emergency Contacts

- Database issues: Check backup restoration procedures
- SSL issues: Contact certificate provider
- Performance issues: Scale up resources or investigate bottlenecks
- Security issues: Review access logs and rotate secrets

## Maintenance

### Regular Tasks

1. **Weekly**: Check backup integrity
2. **Monthly**: Update dependencies and security patches
3. **Quarterly**: Review and rotate secrets
4. **As needed**: Scale resources based on usage patterns

### Updates

1. Test updates in staging environment
2. Create database backup before major updates
3. Deploy during low-traffic periods
4. Monitor application health after deployment
5. Have rollback plan ready

For additional support, refer to the application logs and monitoring dashboards.