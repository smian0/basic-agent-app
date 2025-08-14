# Dokploy Deployment Fix - Using HTTPS with Token

Since Dokploy doesn't support SSH agent forwarding during Docker builds, we need to use HTTPS with a Personal Access Token for private repository access.

## Solution 1: Using GitHub Personal Access Token (Recommended)

### Step 1: Create a GitHub Personal Access Token

1. Go to GitHub: https://github.com/settings/tokens
2. Click **"Generate new token"** → **"Generate new token (classic)"**
3. Give it a name: `Dokploy Deploy Token`
4. Select scopes:
   - ✅ `repo` (Full control of private repositories)
5. Click **"Generate token"**
6. **COPY THE TOKEN IMMEDIATELY** (you won't see it again!)

### Step 2: Update requirements.txt

Change the agno-ck line from SSH to HTTPS with token:

**Current (SSH - doesn't work in Dokploy):**
```
agno-ck @ git+ssh://git@github.com/smian0/agno-ck.git@develop#subdirectory=libs/agno
```

**New (HTTPS with token):**
```
agno-ck @ git+https://YOUR_GITHUB_TOKEN@github.com/smian0/agno-ck.git@develop#subdirectory=libs/agno
```

### Step 3: Secure Token Management in Dokploy

Instead of hardcoding the token, use Dokploy environment variables:

1. In Dokploy, go to your application settings
2. Add environment variable:
   ```
   GITHUB_TOKEN=ghp_YOUR_ACTUAL_TOKEN_HERE
   ```

3. Create a new file `requirements-dokploy.txt`:
   ```bash
   # This file is for Dokploy deployment with token substitution
   # Copy all lines from requirements.txt EXCEPT the agno-ck line
   # Then add this line at the end:
   agno-ck @ git+https://${GITHUB_TOKEN}@github.com/smian0/agno-ck.git@develop#subdirectory=libs/agno
   ```

4. Update Dockerfile to use token substitution:

## Solution 2: Modify Dockerfile for Token Substitution

Create a new `Dockerfile.dokploy`:

```dockerfile
FROM agnohq/python:3.12

# Create app user
RUN groupadd -g 61000 app \
  && useradd -g 61000 -u 61000 -ms /bin/bash -d /app app

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y git openssh-client && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt ./

# Accept GitHub token as build argument
ARG GITHUB_TOKEN

# Replace SSH URL with HTTPS URL using token
RUN if [ -n "$GITHUB_TOKEN" ]; then \
      sed -i "s|git+ssh://git@github.com/|git+https://${GITHUB_TOKEN}@github.com/|g" requirements.txt; \
    fi

# Install Python requirements
RUN uv pip sync requirements.txt --system

# Copy project files
COPY . .

# Change ownership to app user
RUN chown -R app:app /app

# Switch to app user
USER app

# Set Python path
ENV PYTHONPATH=/app

# Command will be overridden by docker-compose.yml
CMD ["echo", "Please specify a command"]
```

Then build with:
```bash
docker build --build-arg GITHUB_TOKEN=ghp_YOUR_TOKEN_HERE -f Dockerfile.dokploy .
```

## Solution 3: Quick Fix - Hardcode Token (NOT RECOMMENDED for production)

If you need a quick fix for testing:

1. Edit `requirements.txt` directly:
   ```
   agno-ck @ git+https://ghp_YOUR_TOKEN_HERE@github.com/smian0/agno-ck.git@develop#subdirectory=libs/agno
   ```

2. **IMPORTANT**: Add `requirements.txt` to `.gitignore` after this change
3. Keep a `requirements.template.txt` without the token for reference

## Solution 4: Use Public Fork (Alternative)

If the repository can be made public or forked publicly:

1. Fork `agno-ck` to a public repository
2. Update `requirements.txt` to use the public fork:
   ```
   agno-ck @ git+https://github.com/YOUR_USERNAME/agno-ck-public.git@develop#subdirectory=libs/agno
   ```

## Recommended Approach for Dokploy

1. **Create GitHub Personal Access Token**
2. **Add token as Dokploy environment variable**
3. **Use Solution 2** - Create `Dockerfile.dokploy` with token substitution
4. **Update docker-compose.yml** to use the new Dockerfile:

```yaml
services:
  api:
    build:
      context: .
      dockerfile: Dockerfile.dokploy
      args:
        GITHUB_TOKEN: ${GITHUB_TOKEN}
```

## Security Notes

- **NEVER** commit tokens to git
- Use environment variables in Dokploy
- Rotate tokens regularly
- Use fine-grained personal access tokens if possible
- Consider using GitHub Apps for production deployments

## Testing Locally

Before deploying to Dokploy, test locally:

```bash
# Set environment variable
export GITHUB_TOKEN=ghp_YOUR_TOKEN_HERE

# Build with token
docker-compose build --build-arg GITHUB_TOKEN=$GITHUB_TOKEN

# Run
docker-compose up
```

This approach works because Dokploy can pass environment variables to the build process, but it cannot forward SSH agents.