# 🐳 Docker Deployment Guide

## Quick Start

### Prerequisites
- Docker Engine 20.10+
- Docker Compose 2.0+
- OpenRouter API key

### One-Command Setup

1. **Set your API key**
```bash
# Edit victim/backend/.env
OPENROUTER_API_KEY=your_actual_api_key_here
VICTIM_MODEL=meta-llama/llama-3.3-70b-instruct
PORT=5000
```

2. **Build and run**
```bash
cd victim
docker-compose up --build
```

3. **Access the application**
- Frontend: http://localhost:8080
- Backend API: http://localhost:5000

### Stop the services
```bash
docker-compose down
```

---

## Services

### Backend (Flask API)
- **Container**: `sentinel-victim-backend`
- **Port**: 5000
- **Base Image**: python:3.12-slim
- **Health Check**: `GET /health` every 30s

### Frontend (Nginx)
- **Container**: `sentinel-victim-frontend`
- **Port**: 8080 (maps to 80 inside container)
- **Base Image**: nginx:alpine
- **Health Check**: HTTP GET every 30s

---

## Docker Commands

### Build services
```bash
docker-compose build
```

### Start services in background
```bash
docker-compose up -d
```

### View logs
```bash
# All services
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Frontend only
docker-compose logs -f frontend
```

### Check service health
```bash
docker-compose ps
```

### Restart services
```bash
docker-compose restart
```

### Stop and remove containers
```bash
docker-compose down
```

### Remove containers and volumes
```bash
docker-compose down -v
```

---

## Development

### Hot Reload (Development Mode)

For development with auto-reload, use volume mounts:

```yaml
# Add to docker-compose.yml
services:
  backend:
    volumes:
      - ./backend:/app
    environment:
      - FLASK_ENV=development

  frontend:
    volumes:
      - ./frontend:/usr/share/nginx/html
```

Then:
```bash
docker-compose up
```

### Build Individual Services

```bash
# Backend only
docker-compose build backend

# Frontend only
docker-compose build frontend
```

---

## Production Deployment

### Environment Variables

Create `.env` file in victim directory:
```env
OPENROUTER_API_KEY=your_production_api_key
VICTIM_MODEL=meta-llama/llama-3.3-70b-instruct
PORT=5000
FLASK_ENV=production
```

### Production Run

```bash
docker-compose -f docker-compose.yml up -d
```

### Resource Limits

Add to docker-compose.yml:
```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

---

## Networking

### Network Architecture

```
┌─────────────────┐
│   User Browser  │
└────────┬────────┘
         │ HTTP :8080
         ▼
┌─────────────────┐
│    Frontend     │
│   (Nginx:80)    │
└────────┬────────┘
         │ HTTP :5000
         ▼
┌─────────────────┐
│     Backend     │
│   (Flask:5000)  │
└────────┬────────┘
         │ HTTPS
         ▼
┌─────────────────┐
│   OpenRouter    │
│   API (LLM)     │
└─────────────────┘
```

### Custom Network

The services communicate via `sentinel-victim-network` bridge network.

Access between services:
- Frontend → Backend: `http://backend:5000`
- External → Frontend: `http://localhost:8080`
- External → Backend: `http://localhost:5000`

---

## Troubleshooting

### Backend won't start

```bash
# Check logs
docker-compose logs backend

# Common issues:
# 1. Missing API key
docker-compose exec backend env | grep OPENROUTER

# 2. Port already in use
netstat -an | findstr :5000  # Windows
lsof -i :5000               # Linux/Mac

# 3. Health check failing
docker-compose exec backend curl http://localhost:5000/health
```

### Frontend can't reach backend

```bash
# Check network connectivity
docker-compose exec frontend ping backend

# Check backend from frontend container
docker-compose exec frontend wget -O- http://backend:5000/health

# Verify nginx config
docker-compose exec frontend nginx -t
```

### Container keeps restarting

```bash
# Check health status
docker inspect sentinel-victim-backend | grep -A 10 Health

# View recent logs
docker logs sentinel-victim-backend --tail 50
```

### Permission errors

```bash
# Linux/Mac: Fix permissions
sudo chown -R $USER:$USER .

# Windows: Run Docker Desktop as Administrator
```

---

## Health Checks

### Automated Health Monitoring

Both services include health checks:

**Backend**:
- Interval: 30 seconds
- Timeout: 10 seconds
- Retries: 3
- Command: `curl -f http://localhost:5000/health`

**Frontend**:
- Interval: 30 seconds
- Timeout: 10 seconds
- Retries: 3
- Command: `wget --spider http://localhost:80/`

### Manual Health Check

```bash
# Backend
curl http://localhost:5000/health

# Frontend
curl http://localhost:8080/

# Via Docker
docker-compose exec backend curl http://localhost:5000/health
```

---

## Scaling

### Horizontal Scaling

```bash
# Run multiple backend instances
docker-compose up --scale backend=3
```

Note: You'll need a load balancer (nginx/traefik) to distribute requests.

---

## Security

### Best Practices

1. **Never commit `.env` files**
2. **Use secrets management in production**
3. **Update base images regularly**
4. **Scan for vulnerabilities**

```bash
# Scan images
docker scan sentinel-victim-backend
docker scan sentinel-victim-frontend
```

5. **Run as non-root user** (add to Dockerfile):
```dockerfile
RUN adduser -D appuser
USER appuser
```

---

## Monitoring

### Container Stats

```bash
# Real-time stats
docker stats

# Specific container
docker stats sentinel-victim-backend
```

### Logs

```bash
# Follow all logs
docker-compose logs -f --tail=100

# Export logs
docker-compose logs > logs.txt
```

---

## Cleanup

### Remove everything

```bash
# Stop and remove containers, networks
docker-compose down

# Also remove volumes
docker-compose down -v

# Remove images
docker rmi sentinel-victim-backend sentinel-victim-frontend
```

### Prune unused resources

```bash
# Remove all unused containers, networks, images
docker system prune -a
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Build and Push Docker Images

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Build images
        run: docker-compose build
      
      - name: Run tests
        run: docker-compose up -d && sleep 10 && curl http://localhost:5000/health
```

---

## Performance Tuning

### Nginx Optimization

Already included in nginx.conf:
- Gzip compression
- Static file caching
- Security headers

### Python Optimization

Add to Dockerfile:
```dockerfile
ENV PYTHONOPTIMIZE=1
```

---

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Flask Deployment](https://flask.palletsprojects.com/en/latest/deploying/)

---

**Built for SENTINEL Project** | Containerized LLM Security Testing Platform
