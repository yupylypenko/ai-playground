#!/bin/bash
# Setup script for k3d cluster
# k3d is a lightweight wrapper to run k3s in Docker

set -e

echo "🚀 Setting up k3d cluster for Cosmic Flight Simulator..."

# Check if k3d is installed
if ! command -v k3d &> /dev/null; then
    echo "❌ k3d is not installed. Please install it first:"
    echo "   curl -s https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh | bash"
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

CLUSTER_NAME="cosmic-flight-sim"

# Check if cluster already exists
if k3d cluster list | grep -q "$CLUSTER_NAME"; then
    echo "⚠️  Cluster '$CLUSTER_NAME' already exists. Deleting it..."
    k3d cluster delete "$CLUSTER_NAME"
fi

# Create k3d cluster with ingress enabled
echo "📦 Creating k3d cluster '$CLUSTER_NAME'..."
k3d cluster create "$CLUSTER_NAME" \
    --port "8080:80@loadbalancer" \
    --port "8443:443@loadbalancer" \
    --wait

echo "✅ k3d cluster created successfully!"
echo ""
echo "📋 Cluster info:"
kubectl cluster-info

echo ""
echo "🔧 Next steps:"
echo "   1. Build and load Docker image:"
echo "      docker build -t cosmic-flight-simulator:latest ."
echo "      k3d image import cosmic-flight-simulator:latest -c $CLUSTER_NAME"
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
