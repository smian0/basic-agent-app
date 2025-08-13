# Docker Compose Multi-Environment Workflow

This project uses Docker Compose with environment-specific override files to manage development and production deployments, mirroring the `ag ws` dev/prod workflow.

## File Structure

```
docker-compose.yml           # Base configuration (shared)
docker-compose.override.yml  # Development overrides (auto-loaded)
docker-compose.prod.yml      # Production configuration
.env                        # Your environment variables (git-ignored)
.env.example                # Template for environment variables
```

## How It Works

### Three-Layer Configuration

1. **Base Layer** (`docker-compose.yml`)
   - Shared configuration for all environments
   - Service definitions without environment-specific settings
   - Common environment variables and dependencies

2. **Development Layer** (`docker-compose.override.yml`)
   - Automatically loaded in development
   - Adds hot reload, debug mode, volume mounts
   - Exposes all ports for local access

3. **Production Layer** (`docker-compose.prod.yml`)
   - Explicitly loaded for production
   - Uses pre-built images instead of building
   - Adds resource limits, replicas, and logging
   - Includes nginx reverse proxy option

## Development Workflow

### Quick Start (Development)
```bash
# Copy environment variables
cp .env.example .env
# Edit .env with your API keys

# Start development environment (auto-loads override)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Development Features
- ✅ Hot reload enabled (code changes reflect immediately)
- ✅ All ports exposed (5432, 8000, 8501)
- ✅ Volume mounts for live code editing
- ✅ Debug mode enabled
- ✅ Single instance of each service

### Development Commands
```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d api

# Rebuild after requirements change
docker-compose build
docker-compose up -d

# View logs
docker-compose logs -f [service]

# Execute commands in container
docker-compose exec api bash
docker-compose exec db psql -U ai -d ai

# Clean everything
docker-compose down -v  # Also removes volumes
```

## Production Workflow

### Production Deployment
```bash
# Build production images
docker-compose -f docker-compose.yml build

# Tag and push to registry (optional)
docker tag basic-agent-app:latest your-registry.com/basic-agent-app:v1.0.0
docker push your-registry.com/basic-agent-app:v1.0.0

# Start production environment
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Scale services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --scale api=3 --scale ui=2
```

### Production Features
- ✅ Pre-built images (no source code needed)
- ✅ Resource limits and reservations
- ✅ Multiple workers and replicas
- ✅ Restart policies
- ✅ Production logging configuration
- ✅ Optional nginx reverse proxy
- ✅ Security-hardened (ports bound to localhost only)

### Production Commands
```bash
# Start production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# View production logs
docker-compose -f docker-compose.yml -f docker-compose.prod.yml logs -f

# Stop production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml down

# Update production images
docker-compose -f docker-compose.yml -f docker-compose.prod.yml pull
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Environment Variables

### Required Variables
- `OPENAI_API_KEY`: OpenAI API key for AI models
- `AGNO_API_KEY`: Agno API key for monitoring

### Optional Variables
- `EXA_API_KEY`: Exa search API (optional)
- `DB_USER`, `DB_PASS`, `DB_DATABASE`: Database credentials
- `DOCKER_REGISTRY`: Docker registry URL (production)
- `DOCKER_IMAGE`: Image name (production)
- `TAG`: Image tag (production)

## Comparison with ag ws

| Feature | Docker Compose | ag ws |
|---------|---------------|-------|
| **Development** | `docker-compose up` | `ag ws up` |
| **Production** | `docker-compose -f ... prod.yml up` | `ag ws up prd` |
| **Configuration** | YAML files | Python files |
| **Hot Reload** | ✅ Volume mounts | ✅ Volume mounts |
| **Multi-Environment** | ✅ Override files | ✅ Python configs |
| **AWS Integration** | ❌ Manual setup | ✅ Built-in ECS |
| **Simplicity** | ✅ Standard Docker | ❌ Custom CLI |
| **Portability** | ✅ Any Docker host | ❌ Agno-specific |

## Best Practices

### Development
1. Always use `.env` for secrets (never commit)
2. Run `docker-compose build` after dependency changes
3. Use `docker-compose logs -f` to debug issues
4. Keep `docker-compose.override.yml` for personal dev preferences

### Production
1. Build and tag images with version numbers
2. Use external database service (RDS, Cloud SQL) for production
3. Set up reverse proxy (nginx, Traefik) for SSL/TLS
4. Configure monitoring and logging (Datadog, CloudWatch)
5. Use secrets management (AWS Secrets Manager, Vault)

## Migration from ag ws

### From ag ws to Docker Compose
```bash
# Stop ag ws
ag ws down

# Start Docker Compose
docker-compose up -d
```

### From Docker Compose to ag ws
```bash
# Stop Docker Compose
docker-compose down

# Remove network if needed
docker network rm agent-app

# Start ag ws
ag ws up
```

## Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   docker-compose down
   docker ps -a  # Check for orphaned containers
   lsof -i :8000  # Check what's using the port
   ```

2. **Module import errors**
   - Ensure `PYTHONPATH=/app` is set in environment
   - Rebuild containers: `docker-compose build`

3. **Database connection errors**
   - Wait for health check: `docker-compose ps`
   - Check logs: `docker-compose logs db`

4. **Permission errors**
   - Check file ownership in mounted volumes
   - Run `docker-compose exec [service] ls -la /app`

## Advanced Usage

### Custom Development Setup
Create `docker-compose.override.yml` with your preferences:
```yaml
services:
  api:
    environment:
      MY_CUSTOM_VAR: value
    ports:
      - "8888:8000"  # Use different port
```

### Production with External Database
Modify `docker-compose.prod.yml`:
```yaml
services:
  # Remove or disable local db service
  # db:
  #   profiles: ["disabled"]
  
  api:
    environment:
      DB_HOST: your-rds-instance.amazonaws.com
      DB_PORT: 5432
      DB_USER: ${PROD_DB_USER}
      DB_PASS: ${PROD_DB_PASS}
```

### Multi-Stage Deployment
```bash
# Staging environment
docker-compose -f docker-compose.yml -f docker-compose.staging.yml up -d

# Production environment
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Summary

This Docker Compose setup provides:
- ✅ **Development**: Simple `docker-compose up` with hot reload
- ✅ **Production**: Hardened configuration with scaling
- ✅ **Flexibility**: Easy to customize for any environment
- ✅ **Compatibility**: Works alongside ag ws
- ✅ **Best Practices**: Follows Docker and cloud-native patterns

The three-file structure (base + override + prod) is a Docker Compose best practice that provides maximum flexibility while keeping configurations DRY (Don't Repeat Yourself).