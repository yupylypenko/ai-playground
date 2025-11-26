#!/bin/bash
# Validate Kubernetes manifests without requiring a running cluster

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🔍 Validating Kubernetes manifests..."
echo ""

# Check if kubectl is available for validation
if ! command -v kubectl &> /dev/null; then
    echo "⚠️  kubectl not found. Installing basic validation..."
    echo "   (Manifests will be checked for basic YAML syntax only)"
fi

VALID=0
INVALID=0

# List of manifest files to validate
MANIFESTS=(
    "namespace.yaml"
    "configmap.yaml"
    "deployment.yaml"
    "service.yaml"
    "ingress.yaml"
    "kustomization.yaml"
)

for manifest in "${MANIFESTS[@]}"; do
    if [ ! -f "$manifest" ]; then
        echo "❌ $manifest: File not found"
        INVALID=$((INVALID + 1))
        continue
    fi

    # Basic YAML syntax check
    if command -v python3 &> /dev/null; then
        if python3 -c "import yaml; yaml.safe_load(open('$manifest'))" 2>/dev/null; then
            echo "✅ $manifest: Valid YAML"
            VALID=$((VALID + 1))
        else
            echo "❌ $manifest: Invalid YAML syntax"
            INVALID=$((INVALID + 1))
        fi
    elif command -v kubectl &> /dev/null; then
        if kubectl apply --dry-run=client -f "$manifest" &> /dev/null; then
            echo "✅ $manifest: Valid Kubernetes manifest"
            VALID=$((VALID + 1))
        else
            echo "❌ $manifest: Invalid Kubernetes manifest"
            kubectl apply --dry-run=client -f "$manifest" 2>&1 | head -5
            INVALID=$((INVALID + 1))
        fi
    else
        # Just check if file exists and is readable
        if [ -r "$manifest" ]; then
            echo "✅ $manifest: File exists and is readable"
            VALID=$((VALID + 1))
        else
            echo "❌ $manifest: Cannot read file"
            INVALID=$((INVALID + 1))
        fi
    fi
done

echo ""
if [ $INVALID -eq 0 ]; then
    echo "✅ All manifests are valid! ($VALID files checked)"
    echo ""
    echo "📋 Next steps to deploy:"
    echo "   1. Ensure Docker Desktop is running (for WSL2)"
    echo "   2. Run: ./k8s/setup-k3d.sh"
    echo "   3. Build image: docker build -t cosmic-flight-simulator:latest ."
    echo "   4. Load image: k3d image import cosmic-flight-simulator:latest -c cosmic-flight-sim"
    echo "   5. Deploy: ./k8s/deploy.sh"
    exit 0
else
    echo "❌ Found $INVALID invalid manifest(s). Please fix them before deploying."
    exit 1
fi
