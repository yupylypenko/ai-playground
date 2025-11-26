#!/bin/bash
# Deployment script for Cosmic Flight Simulator on Kubernetes

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

echo "🚀 Deploying Cosmic Flight Simulator to Kubernetes..."

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed. Please install it first."
    exit 1
fi

# Check if we can connect to cluster
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Cannot connect to Kubernetes cluster. Please check your kubeconfig."
    exit 1
fi

# Check if secret exists, if not create from template
if ! kubectl get secret cosmic-flight-sim-secrets -n cosmic-flight-sim &> /dev/null; then
    echo "⚠️  Secret not found. Creating from template..."
    if [ ! -f "k8s/secret.yaml" ]; then
        cp k8s/secret.yaml.template k8s/secret.yaml
        echo "📝 Created k8s/secret.yaml from template. Please edit it with your values."
        echo "   Then run this script again."
        exit 1
    fi
fi

# Apply all manifests
echo "📦 Applying Kubernetes manifests..."
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml

echo "✅ Deployment complete!"
echo ""
echo "⏳ Waiting for pods to be ready..."
kubectl wait --for=condition=ready pod \
    --selector=app=cosmic-flight-simulator \
    --namespace=cosmic-flight-sim \
    --timeout=120s

echo ""
echo "📊 Deployment status:"
kubectl get pods -n cosmic-flight-sim
kubectl get svc -n cosmic-flight-sim
kubectl get ingress -n cosmic-flight-sim

echo ""
echo "🌐 Access the API:"
echo "   - Service: kubectl port-forward -n cosmic-flight-sim svc/cosmic-flight-simulator-service 8000:80"
echo "   - Then visit: http://localhost:8000/docs"
echo ""
echo "   - Or use ingress (if configured):"
echo "     curl http://cosmic-flight-sim.local/docs"
