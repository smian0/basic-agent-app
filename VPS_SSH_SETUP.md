# VPS GitHub SSH Key Setup Guide

This guide will help you set up SSH keys on your VPS to authenticate with GitHub for pulling private repositories during Docker builds.

## Prerequisites
- SSH access to your VPS
- GitHub account with access to the private repository

## Step 1: Connect to Your VPS

```bash
ssh your-user@your-vps-ip
```

## Step 2: Generate SSH Key on VPS

Generate a new SSH key specifically for GitHub (using ed25519 algorithm for better security):

```bash
ssh-keygen -t ed25519 -C "shoaib@mian.com" -f ~/.ssh/github_deploy
```

**Important:** 
- Press Enter when prompted for a passphrase (leave it empty for automated deployments)
- This creates two files:
  - `~/.ssh/github_deploy` (private key)
  - `~/.ssh/github_deploy.pub` (public key)

## Step 3: Display the Public Key

Copy the public key content that you'll add to GitHub:

```bash
cat ~/.ssh/github_deploy.pub
```

The output will look like:
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAI... shoaib@mian.com
```

**Copy this entire line** - you'll need it in the next step.

## Step 4: Add SSH Key to GitHub

### Option A: Add as Deploy Key (Recommended for single repository)

1. Go to your repository: https://github.com/smian0/agno-ck
2. Navigate to **Settings** → **Deploy keys** (in the left sidebar)
3. Click **Add deploy key**
4. Title: `VPS Docker Build Key` (or any descriptive name)
5. Key: Paste the public key you copied
6. Check **Allow write access** if needed (usually not required for builds)
7. Click **Add key**

### Option B: Add to Your Account (Access to all your repositories)

1. Go to GitHub Settings: https://github.com/settings/keys
2. Click **New SSH key**
3. Title: `VPS Docker Build` (or any descriptive name)
4. Key type: `Authentication key`
5. Key: Paste the public key you copied
6. Click **Add SSH key**

## Step 5: Configure SSH on VPS

Create or edit the SSH config file:

```bash
nano ~/.ssh/config
```

Add the following configuration:

```
Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/github_deploy
    StrictHostKeyChecking no
```

Save and exit (Ctrl+X, then Y, then Enter).

Set proper permissions:

```bash
chmod 600 ~/.ssh/config
chmod 600 ~/.ssh/github_deploy
chmod 644 ~/.ssh/github_deploy.pub
```

## Step 6: Test the Connection

Test that SSH authentication works:

```bash
ssh -T git@github.com
```

You should see:
```
Hi username! You've successfully authenticated, but GitHub does not provide shell access.
```

## Step 7: Configure SSH Agent for Docker Builds

Start the SSH agent and add your key:

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/github_deploy
```

Verify the key is loaded:

```bash
ssh-add -l
```

## Step 8: Build Docker Images with SSH

When building Docker images that need to pull from private repos, use:

```bash
# Using docker-compose
DOCKER_BUILDKIT=1 docker-compose build --ssh default

# Or with docker directly
DOCKER_BUILDKIT=1 docker build --ssh default -t your-image .
```

## Step 9: Make SSH Agent Persistent (Optional)

To ensure SSH agent starts automatically, add to your shell profile:

```bash
echo 'eval "$(ssh-agent -s)" > /dev/null 2>&1' >> ~/.bashrc
echo 'ssh-add ~/.ssh/github_deploy > /dev/null 2>&1' >> ~/.bashrc
source ~/.bashrc
```

## Troubleshooting

### If you get "Permission denied (publickey)"

1. Check if the key is loaded:
   ```bash
   ssh-add -l
   ```

2. Re-add the key:
   ```bash
   ssh-add ~/.ssh/github_deploy
   ```

3. Verify GitHub connection:
   ```bash
   ssh -vT git@github.com
   ```

### If Docker build still fails

1. Ensure BuildKit is enabled:
   ```bash
   export DOCKER_BUILDKIT=1
   ```

2. Check if SSH agent socket is available:
   ```bash
   echo $SSH_AUTH_SOCK
   ```

3. For Dokploy/automated deployments, you might need to:
   - Use a deployment token instead of SSH
   - Or configure the build environment to have SSH access

## Alternative: Using Personal Access Token (If SSH doesn't work)

If SSH setup is problematic, you can modify `requirements.txt` to use HTTPS with a token:

1. Create a GitHub Personal Access Token:
   - Go to https://github.com/settings/tokens
   - Generate new token (classic)
   - Select `repo` scope
   - Copy the token

2. Modify the requirements.txt line from:
   ```
   agno-ck @ git+ssh://git@github.com/smian0/agno-ck.git@develop#subdirectory=libs/agno
   ```
   
   To:
   ```
   agno-ck @ git+https://YOUR_TOKEN@github.com/smian0/agno-ck.git@develop#subdirectory=libs/agno
   ```

3. **Security Note**: Never commit tokens to your repository. Use environment variables or secrets management.

## For Dokploy Specific Setup

Dokploy might handle SSH keys differently. You may need to:

1. Add the SSH private key as a secret in Dokploy
2. Configure the build to use that secret
3. Or switch to HTTPS with deployment tokens

Check Dokploy's documentation for their recommended approach for private repository access.

---

## Summary

After completing these steps, your VPS will be able to:
- Authenticate with GitHub using SSH
- Pull private repositories during Docker builds
- Build images that depend on private GitHub repositories

Remember to keep your private key secure and never share it or commit it to version control.