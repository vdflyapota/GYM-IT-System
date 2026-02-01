# Kubernetes Deployment Guide

## Prerequisites

1. **Kubernetes Cluster**: A running Kubernetes cluster (v1.20+)
   - Local: Minikube, Kind, or Docker Desktop
   - Cloud: GKE, EKS, AKS
   
2. **kubectl**: Kubernetes CLI tool installed and configured

3. **Docker Registry**: Access to a Docker registry for container images
   - Docker Hub
   - Google Container Registry (GCR)
   - Amazon ECR
   - Azure Container Registry

## Build and Push Docker Images

First, build all service images and push them to your registry:

```bash
# Set your registry prefix
export REGISTRY="your-registry.io/gymit"

# Build and push auth-service
docker build -t $REGISTRY/auth-service:latest services/auth-service/
docker push $REGISTRY/auth-service:latest

# Build and push user-service
docker build -t $REGISTRY/user-service:latest services/user-service/
docker push $REGISTRY/user-service:latest

# Build and push tournament-service
docker build -t $REGISTRY/tournament-service:latest services/tournament-service/
docker push $REGISTRY/tournament-service:latest

# Build and push notification-service
docker build -t $REGISTRY/notification-service:latest services/notification-service/
docker push $REGISTRY/notification-service:latest

# Build and push api-gateway
docker build -t $REGISTRY/api-gateway:latest services/api-gateway/
docker push $REGISTRY/api-gateway:latest
```

## Update Kubernetes Manifests

Update the image names in the deployment files to match your registry:

```bash
# Update all deployment files
find k8s/services k8s/gateway -name "*.yaml" -exec sed -i 's|gymit/|your-registry.io/gymit/|g' {} \;
```

## Deploy to Kubernetes

### Step 1: Create Namespace

```bash
kubectl apply -f k8s/namespaces/namespace.yaml
```

### Step 2: Create Secrets

**IMPORTANT**: Update the secrets file with production values before applying!

```bash
# Edit the secrets file
vi k8s/configmaps/secrets.yaml

# Apply secrets
kubectl apply -f k8s/configmaps/secrets.yaml
```

### Step 3: Create ConfigMaps

```bash
kubectl apply -f k8s/configmaps/config.yaml
```

### Step 4: Deploy Databases

```bash
kubectl apply -f k8s/databases/
```

Wait for databases to be ready:

```bash
kubectl wait --for=condition=ready pod -l app=auth-db -n gymit-microservices --timeout=300s
kubectl wait --for=condition=ready pod -l app=user-db -n gymit-microservices --timeout=300s
kubectl wait --for=condition=ready pod -l app=tournament-db -n gymit-microservices --timeout=300s
kubectl wait --for=condition=ready pod -l app=redis -n gymit-microservices --timeout=300s
```

### Step 5: Deploy Services

```bash
kubectl apply -f k8s/services/
```

Wait for services to be ready:

```bash
kubectl wait --for=condition=ready pod -l app=auth-service -n gymit-microservices --timeout=300s
kubectl wait --for=condition=ready pod -l app=user-service -n gymit-microservices --timeout=300s
kubectl wait --for=condition=ready pod -l app=tournament-service -n gymit-microservices --timeout=300s
kubectl wait --for=condition=ready pod -l app=notification-service -n gymit-microservices --timeout=300s
```

### Step 6: Deploy API Gateway

```bash
kubectl apply -f k8s/gateway/
```

Wait for gateway to be ready:

```bash
kubectl wait --for=condition=ready pod -l app=api-gateway -n gymit-microservices --timeout=300s
```

## Verify Deployment

### Check Pod Status

```bash
kubectl get pods -n gymit-microservices
```

All pods should be in "Running" state.

### Check Services

```bash
kubectl get svc -n gymit-microservices
```

### View Logs

```bash
# Auth service logs
kubectl logs -f deployment/auth-service -n gymit-microservices

# User service logs
kubectl logs -f deployment/user-service -n gymit-microservices

# Tournament service logs
kubectl logs -f deployment/tournament-service -n gymit-microservices

# API Gateway logs
kubectl logs -f deployment/api-gateway -n gymit-microservices
```

### Test Health Endpoints

```bash
# Get the LoadBalancer IP or use port-forward
kubectl port-forward svc/api-gateway 8000:80 -n gymit-microservices

# In another terminal, test the endpoints
curl http://localhost:8000/healthz
curl http://localhost:8000/api/auth/health
curl http://localhost:8000/api/users/health
curl http://localhost:8000/api/tournaments/health
curl http://localhost:8000/api/notifications/health
```

## Scaling Services

Scale individual services based on load:

```bash
# Scale tournament service (high load expected)
kubectl scale deployment tournament-service --replicas=5 -n gymit-microservices

# Scale API gateway for load balancing
kubectl scale deployment api-gateway --replicas=5 -n gymit-microservices
```

## Auto-Scaling with HPA

Create Horizontal Pod Autoscaler:

```bash
# Auto-scale tournament service based on CPU
kubectl autoscale deployment tournament-service \
  --cpu-percent=70 \
  --min=2 \
  --max=10 \
  -n gymit-microservices

# Auto-scale API gateway
kubectl autoscale deployment api-gateway \
  --cpu-percent=70 \
  --min=3 \
  --max=10 \
  -n gymit-microservices
```

## Monitoring

### View Resource Usage

```bash
kubectl top pods -n gymit-microservices
kubectl top nodes
```

### Describe Resources

```bash
kubectl describe deployment auth-service -n gymit-microservices
kubectl describe pod <pod-name> -n gymit-microservices
```

## Updating Services

To update a service:

```bash
# Build new image
docker build -t $REGISTRY/auth-service:v2 services/auth-service/
docker push $REGISTRY/auth-service:v2

# Update deployment
kubectl set image deployment/auth-service \
  auth-service=$REGISTRY/auth-service:v2 \
  -n gymit-microservices

# Check rollout status
kubectl rollout status deployment/auth-service -n gymit-microservices

# Rollback if needed
kubectl rollout undo deployment/auth-service -n gymit-microservices
```

## Ingress and TLS

### Install NGINX Ingress Controller

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml
```

### Install cert-manager for TLS

```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
```

### Configure TLS Certificate Issuer

Create a ClusterIssuer for Let's Encrypt:

```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@gym.it
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
```

Apply:

```bash
kubectl apply -f cluster-issuer.yaml
```

### Update Ingress

Update the host in `k8s/gateway/api-gateway.yaml` to your domain, then apply:

```bash
kubectl apply -f k8s/gateway/api-gateway.yaml
```

## Troubleshooting

### Pod Not Starting

```bash
kubectl describe pod <pod-name> -n gymit-microservices
kubectl logs <pod-name> -n gymit-microservices
```

### Database Connection Issues

```bash
# Check database pods
kubectl get pods -l app=auth-db -n gymit-microservices

# Test database connection
kubectl run -it --rm debug --image=postgres:16 --restart=Never -n gymit-microservices -- \
  psql -h auth-db -U authuser -d authdb
```

### Service Communication Issues

```bash
# Test internal service communication
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -n gymit-microservices -- \
  curl http://auth-service:8001/healthz
```

### View Events

```bash
kubectl get events -n gymit-microservices --sort-by='.lastTimestamp'
```

## Production Best Practices

1. **Resource Limits**: Set appropriate CPU and memory limits
2. **Health Checks**: Configure liveness and readiness probes
3. **Rolling Updates**: Use rolling update strategy for zero-downtime deployments
4. **Secrets Management**: Use external secrets management (HashiCorp Vault, AWS Secrets Manager)
5. **Network Policies**: Implement network policies to restrict inter-service communication
6. **Pod Disruption Budgets**: Set PDBs to ensure availability during maintenance
7. **Monitoring**: Deploy Prometheus and Grafana for metrics
8. **Logging**: Use EFK (Elasticsearch, Fluentd, Kibana) stack for centralized logging
9. **Service Mesh**: Consider Istio or Linkerd for advanced traffic management
10. **Backup**: Regular database backups using Velero or native tools

## Clean Up

To remove the entire deployment:

```bash
kubectl delete namespace gymit-microservices
```

Or delete individual components:

```bash
kubectl delete -f k8s/gateway/
kubectl delete -f k8s/services/
kubectl delete -f k8s/databases/
kubectl delete -f k8s/configmaps/
kubectl delete -f k8s/namespaces/
```
