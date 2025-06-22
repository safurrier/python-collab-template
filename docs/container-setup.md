# Container Setup Guide

This project supports both Docker and Podman for containerized development.

## Quick Start

The Makefile automatically detects your container engine:

```bash
# Automatic detection (prefers Podman if available)
make dev-env

# Explicit engine selection
CONTAINER_ENGINE=docker make dev-env
CONTAINER_ENGINE=podman make dev-env
```

## Podman vs Docker

### Key Differences

| Feature | Docker | Podman |
|---------|--------|--------|
| Root privileges | Runs as root by default | Rootless by default |
| Daemon | Requires dockerd daemon | Daemonless |
| Security | Good with proper setup | Better default security |
| Compose support | Native | Via podman-compose |

### When to Use Which

**Use Docker when:**
- It's your team's standard
- You need Docker Desktop features
- You're using Docker-specific tooling

**Use Podman when:**
- Security is a top priority
- You can't/don't want to run a daemon
- You're in a restricted environment

## Troubleshooting

### Permission Issues

If you encounter permission issues with mounted volumes:

1. **For Podman**: Should work automatically with rootless mode
2. **For Docker**: Set your UID/GID in `docker/.env`:
   ```bash
   echo "UID=$(id -u)" >> docker/.env
   echo "GID=$(id -g)" >> docker/.env
   ```

### Socket Issues

If Podman can't find the Docker socket:

```bash
# Set the socket path in your .env
echo "DOCKER_SOCK=${XDG_RUNTIME_DIR}/podman/podman.sock" >> docker/.env
```

### Compose Command Not Found

For Podman, you may need to install podman-compose:

```bash
# macOS
brew install podman-compose

# Linux
pip install podman-compose
```