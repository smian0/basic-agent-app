# Docker Deployment Guide

## Overview

This project uses Docker Compose for **local development** and **local production testing**. For actual cloud deployments, use the appropriate cloud-native tools.

## Local Development (Primary Use)

```bash
# Start development environment
docker-compose up -d

# This automatically uses docker-compose.override.yml which provides:
# - Hot reload (volume mounts)
# - Debug mode
# - Exposed ports for direct access
# - Single instance of each service
```

## Local Production Testing (Optional)

```bash
# Build production image
docker-compose build

# Test with production settings locally
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up

# This uses production settings:
# - Multiple workers
# - No volume mounts (uses built image)
# - Production environment variables
# - Restart policies
```

## Real Production Deployment Options

### Option 1: AWS ECS with ag ws (Recommended)
```bash
# Use Agno's built-in AWS deployment
ag ws up prd

# This handles:
# - ECS Fargate deployment
# - RDS database setup
# - Load balancers
# - Auto-scaling
# - Secrets management
```

### Option 2: Kubernetes
```bash
# Generate Kubernetes manifests from docker-compose
kompose convert

# Or use Helm charts (better for production)
helm install agent-app ./helm-chart
```

### Option 3: Cloud Run (Google Cloud)
```bash
# Deploy to Cloud Run
gcloud run deploy agent-app \
  --image gcr.io/PROJECT/agent-app \
  --platform managed \
  --allow-unauthenticated
```

### Option 4: Fly.io
```bash
# Deploy to Fly.io
fly launch
fly deploy
```

### Option 5: Railway/Render
```bash
# These platforms auto-detect docker-compose.yml
# Just connect your GitHub repo
```

## Do You Need docker-compose.prod.yml?

**Probably not**, unless you:
- Want to test production settings locally
- Are self-hosting on your own servers
- Need to validate production configs before cloud deployment

**For most users**:
- `docker-compose.yml` + `docker-compose.override.yml` for development ✅
- `ag ws up prd` or cloud-specific tools for production ✅
- `docker-compose.prod.yml` is optional ⚠️

## File Structure Explained

```
docker-compose.yml           # Base config (always used)
docker-compose.override.yml  # Dev overrides (auto-loaded)
docker-compose.prod.yml      # Production testing (optional)
```

## Why This Setup?

1. **Development First**: Most time is spent in development
2. **Cloud Native**: Production uses cloud services (ECS, K8s, etc.)
3. **Simplicity**: Avoid over-engineering for edge cases
4. **Flexibility**: Can add production testing if needed

## Quick Commands

### Development (99% of usage)
```bash
docker-compose up -d     # Start
docker-compose logs -f   # Logs
docker-compose down      # Stop
```

### Production Testing (rare)
```bash
# Only if you need to test production settings locally
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up
```

### Real Production (use cloud tools)
```bash
# AWS ECS
ag ws up prd

# Or deploy to your cloud platform of choice
```

## Summary

- **Keep it simple**: Focus on development workflow
- **Use cloud tools**: For real production deployments
- **docker-compose.prod.yml**: Optional, only for local testing
- **Best practice**: Dev locally, deploy to cloud