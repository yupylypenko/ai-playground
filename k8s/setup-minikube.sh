#!/bin/bash
# Setup script for minikube cluster

set -e

echo "🚀 Setting up minikube cluster for Cosmic Flight Simulator..."

# Check if minikube is installed
if ! command -v minikube &> /dev/null; then
    echo "❌ minikube is not installed. Please install it first:"
    echo "   Visit: https://minikube.sigs.k8s.io/docs/start/"
    exit 1
fi

# Start minikube cluster
echo "📦 Starting minikube cluster..."
minikube start

# Enable ingress addon
echo "🔧 Enabling ingress addon..."
minikube addons enable ingress

echo "✅ minikube cluster is ready!"
echo ""
echo "📋 Cluster info:"
kubectl cluster-info

echo ""
echo "🔧 Next steps:"
echo "   1. Build Docker image in minikube:"
echo "      eval \$(minikube docker-env)"
echo "      docker build -t cosmic-flight-simulator:latest ."
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
echo "      minikube service cosmic-flight-simulator-service -n cosmic-flight-sim"
echo "      # Or get the URL:"
echo "      minikube service cosmic-flight-simulator-service -n cosmic-flight-sim --url"
