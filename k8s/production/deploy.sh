#!/bin/bash

# GYM-IT System Kubernetes Deployment Script
# This script deploys the GYM-IT microservices to Kubernetes

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="gymit"
MANIFEST_DIR="$(dirname "$0")"

echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}GYM-IT Kubernetes Deployment Script${NC}"
echo -e "${GREEN}=====================================${NC}"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

if ! command_exists kubectl; then
    echo -e "${RED}Error: kubectl is not installed${NC}"
    exit 1
fi

if ! command_exists docker; then
    echo -e "${YELLOW}Warning: docker is not installed (needed for building images)${NC}"
fi

echo -e "${GREEN}✓ Prerequisites check passed${NC}"
echo ""

# Check cluster connectivity
echo -e "${YELLOW}Checking cluster connectivity...${NC}"
if ! kubectl cluster-info &>/dev/null; then
    echo -e "${RED}Error: Cannot connect to Kubernetes cluster${NC}"
    echo ""
    echo -e "${YELLOW}This script requires a running Kubernetes cluster.${NC}"
    echo ""
    echo "Options to set up a Kubernetes cluster:"
    echo ""
    echo "1. Local Development (Minikube):"
    echo -e "   ${GREEN}minikube start --cpus=4 --memory=8192${NC}"
    echo ""
    echo "2. Local Development (Kind):"
    echo -e "   ${GREEN}kind create cluster --name gymit${NC}"
    echo ""
    echo "3. Cloud Providers:"
    echo -e "   - Google GKE:  ${GREEN}gcloud container clusters create gymit --num-nodes=3${NC}"
    echo -e "   - AWS EKS:     ${GREEN}eksctl create cluster --name gymit --nodes=3${NC}"
    echo -e "   - Azure AKS:   ${GREEN}az aks create --name gymit --node-count 3${NC}"
    echo ""
    echo "4. Verify cluster access:"
    echo -e "   ${GREEN}kubectl cluster-info${NC}"
    echo -e "   ${GREEN}kubectl get nodes${NC}"
    echo ""
    echo -e "${YELLOW}For documentation/review purposes only:${NC}"
    echo "You can review the manifests in this directory without deploying."
    echo ""
    exit 1
fi
echo -e "${GREEN}✓ Connected to cluster: $(kubectl config current-context)${NC}"
echo ""

# Check for metrics server (needed for HPA)
echo -e "${YELLOW}Checking for Metrics Server...${NC}"
if ! kubectl get deployment metrics-server -n kube-system &>/dev/null; then
    echo -e "${YELLOW}Warning: Metrics Server not found. HPA won't work without it.${NC}"
    echo "Install with: kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml"
else
    echo -e "${GREEN}✓ Metrics Server found${NC}"
fi
echo ""

# Deployment confirmation
echo -e "${YELLOW}This will deploy GYM-IT System to namespace: ${NAMESPACE}${NC}"
echo -e "${YELLOW}Current context: $(kubectl config current-context)${NC}"
echo ""
read -p "Continue with deployment? (yes/no): " -r
if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo "Deployment cancelled"
    exit 0
fi
echo ""

# Step 1: Create namespace
echo -e "${YELLOW}Step 1: Creating namespace...${NC}"
kubectl apply -f "$MANIFEST_DIR/00-namespace.yaml"
echo -e "${GREEN}✓ Namespace created${NC}"
echo ""

# Step 2: Apply ConfigMaps and Secrets
echo -e "${YELLOW}Step 2: Applying ConfigMaps and Secrets...${NC}"
kubectl apply -f "$MANIFEST_DIR/01-configmap.yaml"
kubectl apply -f "$MANIFEST_DIR/02-secrets.yaml"
echo -e "${GREEN}✓ Configuration applied${NC}"
echo ""

# Step 3: Deploy databases
echo -e "${YELLOW}Step 3: Deploying databases...${NC}"
kubectl apply -f "$MANIFEST_DIR/03-databases.yaml"
echo "Waiting for databases to be ready (this may take a few minutes)..."
kubectl wait --for=condition=ready pod -l app=auth-db -n $NAMESPACE --timeout=300s || echo "Auth DB timeout"
kubectl wait --for=condition=ready pod -l app=user-db -n $NAMESPACE --timeout=300s || echo "User DB timeout"
kubectl wait --for=condition=ready pod -l app=tournament-db -n $NAMESPACE --timeout=300s || echo "Tournament DB timeout"
kubectl wait --for=condition=ready pod -l app=redis -n $NAMESPACE --timeout=300s || echo "Redis timeout"
echo -e "${GREEN}✓ Databases deployed${NC}"
echo ""

# Step 4: Deploy application services
echo -e "${YELLOW}Step 4: Deploying application services...${NC}"
kubectl apply -f "$MANIFEST_DIR/04-api-gateway.yaml"
kubectl apply -f "$MANIFEST_DIR/05-auth-service.yaml"
kubectl apply -f "$MANIFEST_DIR/06-user-service.yaml"
kubectl apply -f "$MANIFEST_DIR/07-tournament-service.yaml"
kubectl apply -f "$MANIFEST_DIR/08-notification-service.yaml"
echo "Waiting for services to be ready..."
sleep 10
kubectl wait --for=condition=available deployment --all -n $NAMESPACE --timeout=300s || echo "Some deployments not ready"
echo -e "${GREEN}✓ Application services deployed${NC}"
echo ""

# Step 5: Deploy Ingress
echo -e "${YELLOW}Step 5: Deploying Ingress...${NC}"
kubectl apply -f "$MANIFEST_DIR/09-ingress.yaml"
echo -e "${GREEN}✓ Ingress deployed${NC}"
echo ""

# Step 6: Apply Network Policies
echo -e "${YELLOW}Step 6: Applying Network Policies...${NC}"
kubectl apply -f "$MANIFEST_DIR/10-network-policies.yaml"
echo -e "${GREEN}✓ Network Policies applied${NC}"
echo ""

# Display deployment status
echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}Deployment Summary${NC}"
echo -e "${GREEN}=====================================${NC}"
echo ""

echo -e "${YELLOW}Pods:${NC}"
kubectl get pods -n $NAMESPACE

echo ""
echo -e "${YELLOW}Services:${NC}"
kubectl get svc -n $NAMESPACE

echo ""
echo -e "${YELLOW}Horizontal Pod Autoscalers:${NC}"
kubectl get hpa -n $NAMESPACE

echo ""
echo -e "${YELLOW}Ingress:${NC}"
kubectl get ingress -n $NAMESPACE

echo ""
echo -e "${YELLOW}Persistent Volume Claims:${NC}"
kubectl get pvc -n $NAMESPACE

echo ""
echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}=====================================${NC}"
echo ""

# Get Ingress IP
INGRESS_IP=$(kubectl get ingress gymit-ingress -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null)
if [ -z "$INGRESS_IP" ]; then
    INGRESS_IP=$(kubectl get ingress gymit-ingress -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null)
fi

if [ -n "$INGRESS_IP" ]; then
    echo -e "${YELLOW}Ingress LoadBalancer:${NC} $INGRESS_IP"
    echo ""
    echo "Configure your DNS to point to this IP:"
    echo "  gymit.example.com -> $INGRESS_IP"
    echo "  www.gymit.example.com -> $INGRESS_IP"
else
    echo -e "${YELLOW}Note: Ingress LoadBalancer IP not yet assigned${NC}"
    echo "Run 'kubectl get ingress -n gymit' to check status"
fi

echo ""
echo -e "${YELLOW}Useful commands:${NC}"
echo "  View pods:        kubectl get pods -n $NAMESPACE"
echo "  View logs:        kubectl logs -f deployment/api-gateway -n $NAMESPACE"
echo "  View HPA status:  kubectl get hpa -n $NAMESPACE -w"
echo "  Scale service:    kubectl scale deployment api-gateway -n $NAMESPACE --replicas=10"
echo ""

echo -e "${GREEN}Happy deploying!${NC}"
