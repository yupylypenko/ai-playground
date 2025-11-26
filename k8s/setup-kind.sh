#!/bin/bash
# Setup script for kind (Kubernetes in Docker) cluster

set -e

echo "🚀 Setting up kind cluster for Cosmic Flight Simulator..."

# Check if kind is installed
if ! command -v kind &> /dev/null; then
    echo "❌ kind is not installed. Please install it first:"
    echo "   Visit: https://kind.sigs.k8s.io/docs/user/quick-start/#installation"
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

CLUSTER_NAME="cosmic-flight-sim"

# Check if cluster already exists
if kind get clusters | grep -q "$CLUSTER_NAME"; then
    echo "⚠️  Cluster '$CLUSTER_NAME' already exists. Deleting it..."
    kind delete cluster --name "$CLUSTER_NAME"
fi

# Create kind cluster configuration with ingress
cat <<EOF | kind create cluster --name "$CLUSTER_NAME" --config=-
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
  kubeadmConfigPatches:
  - |
    kind: InitConfiguration
    nodeRegistration:
      kubeletExtraArgs:
        node-labels: "ingress-ready=true"
  extraPortMappings:
  - containerPort: 80
    hostPort: 8080
    protocol: TCP
  - containerPort: 443
    hostPort: 8443
    protocol: TCP
EOF

# Install ingress-nginx
echo "🔧 Installing ingress-nginx..."
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml

# Wait for ingress to be ready
echo "⏳ Waiting for ingress controller to be ready..."
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=90s

echo "✅ kind cluster created successfully!"
echo ""
echo "📋 Cluster info:"
kubectl cluster-info --context kind-$CLUSTER_NAME

echo ""
echo "🔧 Next steps:"
echo "   1. Build and load Docker image:"
echo "      docker build -t cosmic-flight-simulator:latest ."
echo "      kind load docker-image cosmic-flight-simulator:latest --name $CLUSTER_NAME"
echo ""
echo "   2. Create secret from template:"
echo "      cp k8s/secret.yaml.template k8s/secret.yaml"
echo "      # Edit k8s/secret.yaml with your values"
echo "      kubectl apply -f k8s/secret.yaml"
echo ""
echo "   3. Deploy application:"
echo "      kubectl apply -f k8s/"
echo ""
echo "   4. Check status:"
echo "      kubectl get pods -n cosmic-flight-sim"
echo "      kubectl get svc -n cosmic-flight-sim"
echo ""
echo "   5. Access the API:"
echo "      curl http://localhost:8080/docs"
echo "      # Or add to /etc/hosts: 127.0.0.1 cosmic-flight-sim.local"
echo "      curl http://cosmic-flight-sim.local/docs"
