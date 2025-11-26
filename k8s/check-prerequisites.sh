#!/bin/bash
# Prerequisites check script for Kubernetes deployment

set -e

echo "🔍 Checking prerequisites for Kubernetes deployment..."
echo ""

MISSING=0

# Check Docker
if command -v docker &> /dev/null; then
    if docker info &> /dev/null; then
        echo "✅ Docker: installed and running"
    else
        echo "⚠️  Docker: installed but not running"
        echo "   Please start Docker: sudo systemctl start docker (Linux) or start Docker Desktop"
        MISSING=$((MISSING + 1))
    fi
else
    echo "❌ Docker: not installed"
    echo "   Install: https://docs.docker.com/get-docker/"
    MISSING=$((MISSING + 1))
fi

# Check kubectl
if command -v kubectl &> /dev/null; then
    echo "✅ kubectl: installed"
    kubectl version --client --short 2>/dev/null || echo "   (version check failed)"
else
    echo "❌ kubectl: not installed"
    echo "   Install: https://kubernetes.io/docs/tasks/tools/"
    MISSING=$((MISSING + 1))
fi

# Check for Kubernetes tools
echo ""
echo "📦 Checking Kubernetes cluster tools..."

if command -v k3d &> /dev/null; then
    echo "✅ k3d: installed"
    k3d version 2>/dev/null | head -1 || true
elif command -v minikube &> /dev/null; then
    echo "✅ minikube: installed"
    minikube version 2>/dev/null | head -1 || true
elif command -v kind &> /dev/null; then
    echo "✅ kind: installed"
    kind version 2>/dev/null || true
else
    echo "❌ No Kubernetes cluster tool found"
    echo ""
    echo "   Install one of the following:"
    echo "   - k3d (recommended): curl -s https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh | bash"
    echo "   - minikube: https://minikube.sigs.k8s.io/docs/start/"
    echo "   - kind: https://kind.sigs.k8s.io/docs/user/quick-start/#installation"
    MISSING=$((MISSING + 1))
fi

echo ""
if [ $MISSING -eq 0 ]; then
    echo "✅ All prerequisites are met!"
    echo ""
    echo "🚀 Ready to deploy. Run:"
    echo "   ./k8s/deploy.sh"
else
    echo "❌ Missing $MISSING prerequisite(s). Please install them first."
    exit 1
fi
