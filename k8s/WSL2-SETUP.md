# WSL2 Setup Guide for Kubernetes Deployment

This guide helps you set up Kubernetes deployment in WSL2 (Windows
Subsystem for Linux).

## Prerequisites for WSL2

### 1. Docker Desktop for Windows

Docker Desktop must be installed and running on Windows:

1. **Install Docker Desktop**: Download from <https://www.docker.com/products/docker-desktop>
2. **Enable WSL2 Integration**:
   - Open Docker Desktop
   - Go to Settings → Resources → WSL Integration
   - Enable integration for your WSL2 distribution
   - Click "Apply & Restart"

3. **Verify Docker in WSL2**:

   ```bash
   docker --version
   docker info
   ```

### 2. Install kubectl

```bash
# Download kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"

# Install
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Verify
kubectl version --client
```

### 3. Install k3d (Recommended)

```bash
curl -s https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh | bash
k3d --version
```

## Quick Start

Once Docker Desktop is running and integrated with WSL2:

```bash
# 1. Navigate to project directory
cd /mnt/d/git/ai-playground

# 2. Validate manifests
./k8s/validate-manifests.sh

# 3. Setup k3d cluster
./k8s/setup-k3d.sh

# 4. Build Docker image
docker build -t cosmic-flight-simulator:latest .

# 5. Load image into k3d
k3d image import cosmic-flight-simulator:latest -c cosmic-flight-sim

# 6. Create secret from template
cp k8s/secret.yaml.template k8s/secret.yaml
# Edit k8s/secret.yaml if needed (optional)

# 7. Deploy application
./k8s/deploy.sh

# 8. Access the API
curl http://localhost:8080/docs
```

## Troubleshooting

### Docker Command Not Found

If `docker` command is not found in WSL2:

1. Ensure Docker Desktop is running on Windows
2. Check WSL2 integration is enabled in Docker Desktop settings
3. Restart WSL2: `wsl --shutdown` (from Windows PowerShell), then reopen WSL2
4. Verify: `docker info`

### Docker Daemon Not Running

If you see "Cannot connect to the Docker daemon":

1. Start Docker Desktop on Windows
2. Wait for it to fully start (whale icon in system tray)
3. Check integration: Docker Desktop → Settings → Resources → WSL Integration

### k3d Cluster Creation Fails

If k3d cannot create cluster:

1. Verify Docker is working: `docker ps`
2. Check Docker context: `docker context ls`
3. Try creating cluster manually:

   ```bash
   k3d cluster create cosmic-flight-sim \
     --port "8080:80@loadbalancer" \
     --wait
   ```

### Port Already in Use

If port 8080 is already in use:

1. Find what's using it: `netstat -tulpn | grep 8080`
2. Change port in setup script or use different port:

   ```bash
   k3d cluster create cosmic-flight-sim \
     --port "3000:80@loadbalancer" \
     --wait
   ```

## Alternative: Use Docker Desktop Kubernetes

If you prefer using Docker Desktop's built-in Kubernetes:

1. Enable Kubernetes in Docker Desktop:
   - Settings → Kubernetes → Enable Kubernetes
   - Click "Apply & Restart"

2. Use kubectl with Docker Desktop context:

   ```bash
   kubectl config use-context docker-desktop
   ```

3. Deploy using the manifests:

   ```bash
   kubectl apply -f k8s/
   ```

## Validation Without Cluster

You can validate manifests without a running cluster:

```bash
./k8s/validate-manifests.sh
```

This checks YAML syntax and basic Kubernetes manifest structure.
