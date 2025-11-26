# Kubernetes Deployment Guide

This directory contains Kubernetes manifests and setup scripts for deploying the
Cosmic Flight Simulator to a local Kubernetes cluster using k3d, minikube, or
kind.

## Prerequisites

- Docker installed and running
- kubectl installed
- One of the following Kubernetes distributions:
  - [k3d](https://k3d.io/) (recommended for simplicity)
  - [minikube](https://minikube.sigs.k8s.io/)
  - [kind](https://kind.sigs.k8s.io/) (Kubernetes in Docker)

## Quick Start

### Option 1: k3d (Recommended)

```bash
# 1. Setup k3d cluster
chmod +x k8s/setup-k3d.sh
./k8s/setup-k3d.sh

# 2. Build and load Docker image
docker build -t cosmic-flight-simulator:latest .
k3d image import cosmic-flight-simulator:latest -c cosmic-flight-sim

# 3. Create secret from template
cp k8s/secret.yaml.template k8s/secret.yaml
# Edit k8s/secret.yaml with your values (optional)

# 4. Deploy application
chmod +x k8s/deploy.sh
./k8s/deploy.sh

# 5. Access the API
curl http://localhost:8080/docs
```

### Option 2: minikube

```bash
# 1. Setup minikube cluster
chmod +x k8s/setup-minikube.sh
./k8s/setup-minikube.sh

# 2. Build Docker image in minikube
eval $(minikube docker-env)
docker build -t cosmic-flight-simulator:latest .

# 3. Create secret from template
cp k8s/secret.yaml.template k8s/secret.yaml
# Edit k8s/secret.yaml with your values (optional)

# 4. Deploy application
chmod +x k8s/deploy.sh
./k8s/deploy.sh

# 5. Access the API
minikube service cosmic-flight-simulator-service -n cosmic-flight-sim
```

### Option 3: kind

```bash
# 1. Setup kind cluster
chmod +x k8s/setup-kind.sh
./k8s/setup-kind.sh

# 2. Build and load Docker image
docker build -t cosmic-flight-simulator:latest .
kind load docker-image cosmic-flight-simulator:latest --name cosmic-flight-sim

# 3. Create secret from template
cp k8s/secret.yaml.template k8s/secret.yaml
# Edit k8s/secret.yaml with your values (optional)

# 4. Deploy application
chmod +x k8s/deploy.sh
./k8s/deploy.sh

# 5. Access the API
curl http://localhost:8080/docs
# Or add to /etc/hosts: 127.0.0.1 cosmic-flight-sim.local
curl http://cosmic-flight-sim.local/docs
```

## Manual Deployment

If you prefer to deploy manually:

```bash
# 1. Create namespace
kubectl apply -f k8s/namespace.yaml

# 2. Create ConfigMap
kubectl apply -f k8s/configmap.yaml

# 3. Create Secret (from template)
cp k8s/secret.yaml.template k8s/secret.yaml
# Edit k8s/secret.yaml with your values
kubectl apply -f k8s/secret.yaml

# 4. Deploy application
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml

# 5. Check status
kubectl get pods -n cosmic-flight-sim
kubectl get svc -n cosmic-flight-sim
```

## Configuration

### ConfigMap (`configmap.yaml`)

Contains non-sensitive configuration:

- MongoDB host and port
- Database name
- API token expiration time
- Python environment variables

### Secret (`secret.yaml.template`)

Contains sensitive data. **You must create `secret.yaml` from the template**:

```bash
cp k8s/secret.yaml.template k8s/secret.yaml
# Edit k8s/secret.yaml with your actual values
```

**Important**: Change `API_SECRET_KEY` in production!

### Environment Variables

The application supports the following environment variables:

- `MONGODB_URI` - Full MongoDB connection string (overrides host/port)
- `MONGODB_HOST` - MongoDB host (default: localhost)
- `MONGODB_PORT` - MongoDB port (default: 27017)
- `MONGODB_DATABASE` - Database name (default: cosmic_flight_sim)
- `MONGODB_USERNAME` - MongoDB username (optional)
- `MONGODB_PASSWORD` - MongoDB password (optional)
- `API_SECRET_KEY` - Secret key for JWT tokens (required)
- `ACCESS_TOKEN_MIN` - Token expiration in minutes (default: 60)

## Accessing the Application

### Port Forwarding

```bash
kubectl port-forward -n cosmic-flight-sim svc/cosmic-flight-simulator-service 8000:80
# Then visit: http://localhost:8000/docs
```

### Ingress

If ingress is configured, you can access via:

- k3d: `http://localhost:8080/docs`
- kind: `http://localhost:8080/docs` or `http://cosmic-flight-sim.local/docs`
- minikube: Use `minikube service` command

### Service URL

```bash
# Get service URL
kubectl get svc -n cosmic-flight-sim

# For minikube
minikube service cosmic-flight-simulator-service -n cosmic-flight-sim --url
```

## Monitoring and Debugging

### Check Pod Status

```bash
kubectl get pods -n cosmic-flight-sim
kubectl describe pod <pod-name> -n cosmic-flight-sim
```

### View Logs

```bash
# All pods
kubectl logs -f -l app=cosmic-flight-simulator -n cosmic-flight-sim

# Specific pod
kubectl logs -f <pod-name> -n cosmic-flight-sim
```

### Check Events

```bash
kubectl get events -n cosmic-flight-sim --sort-by='.lastTimestamp'
```

### Exec into Pod

```bash
kubectl exec -it <pod-name> -n cosmic-flight-sim -- /bin/bash
```

## Scaling

Scale the deployment:

```bash
kubectl scale deployment cosmic-flight-simulator -n cosmic-flight-sim --replicas=3
```

## Updating the Deployment

After building a new Docker image:

```bash
# For k3d
docker build -t cosmic-flight-simulator:latest .
k3d image import cosmic-flight-simulator:latest -c cosmic-flight-sim
kubectl rollout restart deployment cosmic-flight-simulator -n cosmic-flight-sim

# For minikube
eval $(minikube docker-env)
docker build -t cosmic-flight-simulator:latest .
kubectl rollout restart deployment cosmic-flight-simulator -n cosmic-flight-sim

# For kind
docker build -t cosmic-flight-simulator:latest .
kind load docker-image cosmic-flight-simulator:latest --name cosmic-flight-sim
kubectl rollout restart deployment cosmic-flight-simulator -n cosmic-flight-sim
```

## Cleanup

### Delete Deployment

```bash
kubectl delete -f k8s/
```

### Delete Cluster

```bash
# k3d
k3d cluster delete cosmic-flight-sim

# minikube
minikube delete

# kind
kind delete cluster --name cosmic-flight-sim
```

## Troubleshooting

### Pods Not Starting

1. Check pod status: `kubectl get pods -n cosmic-flight-sim`
2. Describe pod: `kubectl describe pod <pod-name> -n cosmic-flight-sim`
3. Check logs: `kubectl logs <pod-name> -n cosmic-flight-sim`

### Image Pull Errors

- Ensure Docker image is built and loaded into the cluster
- For k3d: `k3d image import cosmic-flight-simulator:latest -c cosmic-flight-sim`
- For minikube: Build inside minikube's Docker daemon
- For kind: `kind load docker-image cosmic-flight-simulator:latest --name cosmic-flight-sim`

### Connection Issues

- Verify service is running: `kubectl get svc -n cosmic-flight-sim`
- Check ingress: `kubectl get ingress -n cosmic-flight-sim`
- Test port forwarding:
  `kubectl port-forward -n cosmic-flight-sim svc/cosmic-flight-simulator-service 8000:80`

### MongoDB Connection Issues

- If using external MongoDB, ensure the service is accessible from
  pods:
- Check ConfigMap and Secret values
- Verify network policies allow MongoDB access

## Production Considerations

For production deployments:

1. **Change API_SECRET_KEY** in `secret.yaml`
2. **Use proper MongoDB** with authentication
3. **Configure resource limits** appropriately
4. **Set up monitoring** and logging
5. **Use TLS/HTTPS** for ingress
6. **Configure backup** for MongoDB
7. **Set up horizontal pod autoscaling** (HPA)
8. **Use persistent volumes** for MongoDB if running in-cluster

## Files

- `namespace.yaml` - Kubernetes namespace
- `configmap.yaml` - Non-sensitive configuration
- `secret.yaml.template` - Secret template (copy to `secret.yaml`)
- `deployment.yaml` - Application deployment
- `service.yaml` - Service definition
- `ingress.yaml` - Ingress configuration
- `setup-k3d.sh` - k3d cluster setup script
- `setup-minikube.sh` - minikube cluster setup script
- `setup-kind.sh` - kind cluster setup script
- `deploy.sh` - Deployment script
