#!/bin/bash
echo "🚀 Deploying Load Testing Infrastructure..."
kubectl apply -f artillery-config.yml
kubectl apply -f k6-load-test.js
echo "✅ Load Testing configurado com sucesso!"
# Set error handling
set -euo pipefail

# Define color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Function to handle errors
handle_error() {
    echo -e "${RED}❌ Deployment failed: $1${NC}"
    exit 1
}

# Function to check kubectl availability
check_kubectl() {
    if ! command -v kubectl &> /dev/null; then
        handle_error "kubectl is not installed"
    fi
}

# Function to verify cluster connection
verify_cluster() {
    kubectl cluster-info &> /dev/null || handle_error "Cannot connect to Kubernetes cluster"
}

# Main deployment function
deploy_load_testing() {
    echo -e "${GREEN}📡 Verifying cluster connection...${NC}"
    verify_cluster

    echo -e "${GREEN}🔍 Validating configuration files...${NC}"
    kubectl apply --validate=true --dry-run=client -f artillery-config.yml || handle_error "Invalid artillery configuration"
    kubectl apply --validate=true --dry-run=client -f k6-load-test.js || handle_error "Invalid k6 configuration"

    echo -e "${GREEN}🧹 Cleaning up previous deployments...${NC}"
    kubectl delete -f artillery-config.yml --ignore-not-found
    kubectl delete -f k6-load-test.js --ignore-not-found

    echo -e "${GREEN}⚡ Starting deployment...${NC}"
    kubectl apply -f artillery-config.yml --record
    kubectl apply -f k6-load-test.js --record

    echo -e "${GREEN}✅ Load Testing infrastructure deployed successfully!${NC}"
}

# Execute main function
check_kubectl
deploy_load_testing