# Kubernetes Production Deployment for GYM-IT System

## Overview

This directory contains production-ready Kubernetes manifests for deploying the GYM-IT System microservices architecture with support for 5x growth scalability.

## Architecture

### Microservices
- **API Gateway** (5-15 replicas): Entry point for all requests
- **Auth Service** (3-10 replicas): Authentication and JWT management
- **User Service** (3-10 replicas): User profile management
- **Tournament Service** (5-15 replicas): Tournament and bracket management
- **Notification Service** (3-10 replicas): Real-time notifications via WebSocket

### Databases
- **PostgreSQL** (3 instances): Separate databases for auth, user, and tournament services
- **Redis** (1 instance): Shared cache and pub/sub

### Scalability Features

#### 5x Growth Support
- **Baseline capacity**: ~100-200 concurrent users
- **5x capacity**: ~500-1000 concurrent users
- **Auto-scaling**: HPA configured to handle traffic spikes
- **Resource management**: Proper requests/limits for efficient scheduling

#### Scaling Configuration
| Service | Min Replicas | Max Replicas | CPU Request | Memory Request |
|---------|--------------|--------------|-------------|----------------|
| API Gateway | 5 | 15 | 250m | 256Mi |
| Auth Service | 3 | 10 | 200m | 256Mi |
| User Service | 3 | 10 | 200m | 256Mi |
| Tournament Service | 5 | 15 | 300m | 512Mi |
| Notification Service | 3 | 10 | 200m | 256Mi |

Total minimum resources required:
- **CPU**: ~3.5 cores
- **Memory**: ~5GB
- **Storage**: ~45GB (databases + Redis)

## Prerequisites

1. **Kubernetes Cluster** (v1.24+)
   - Managed service (GKE, EKS, AKS) or self-hosted
   - At least 3 worker nodes with 4 CPU cores and 8GB RAM each

2. **kubectl** installed and configured

3. **Ingress Controller** (NGINX recommended)
   ```bash
   kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml
   ```

4. **cert-manager** for SSL/TLS certificates
   ```bash
   kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
   ```

5. **Metrics Server** for HPA
   ```bash
   kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
   ```

## Deployment Instructions

### Step 1: Update Configuration

1. **Edit secrets** (02-secrets.yaml):
   ```bash
   # Generate secure random keys
   SECRET_KEY=$(openssl rand -hex 32)
   JWT_SECRET_KEY=$(openssl rand -hex 32)
   
   # Update the secrets file with real values
   # IMPORTANT: Never commit real secrets to version control!
   ```

2. **Update Ingress domain** (09-ingress.yaml):
   ```yaml
   # Replace gymit.example.com with your actual domain
   ```

### Step 2: Build and Push Docker Images

```bash
# Build images for each service
cd services/api-gateway
docker build -t <your-registry>/gymit-api-gateway:latest .
docker push <your-registry>/gymit-api-gateway:latest

cd ../auth-service
docker build -t <your-registry>/gymit-auth-service:latest .
docker push <your-registry>/gymit-auth-service:latest

cd ../user-service
docker build -t <your-registry>/gymit-user-service:latest .
docker push <your-registry>/gymit-user-service:latest

cd ../tournament-service
docker build -t <your-registry>/gymit-tournament-service:latest .
docker push <your-registry>/gymit-tournament-service:latest

cd ../notification-service
docker build -t <your-registry>/gymit-notification-service:latest .
docker push <your-registry>/gymit-notification-service:latest
```

Update the image references in deployment files to use your registry.

### Step 3: Deploy to Kubernetes

```bash
# Navigate to production manifests directory
cd k8s/production

# Apply manifests in order
kubectl apply -f 00-namespace.yaml
kubectl apply -f 01-configmap.yaml
kubectl apply -f 02-secrets.yaml
kubectl apply -f 03-databases.yaml

# Wait for databases to be ready
kubectl wait --for=condition=ready pod -l app=auth-db -n gymit --timeout=300s
kubectl wait --for=condition=ready pod -l app=user-db -n gymit --timeout=300s
kubectl wait --for=condition=ready pod -l app=tournament-db -n gymit --timeout=300s
kubectl wait --for=condition=ready pod -l app=redis -n gymit --timeout=300s

# Deploy services
kubectl apply -f 04-api-gateway.yaml
kubectl apply -f 05-auth-service.yaml
kubectl apply -f 06-user-service.yaml
kubectl apply -f 07-tournament-service.yaml
kubectl apply -f 08-notification-service.yaml

# Deploy ingress and network policies
kubectl apply -f 09-ingress.yaml
kubectl apply -f 10-network-policies.yaml

# Verify deployment
kubectl get all -n gymit
```

### Step 4: Configure DNS

Point your domain to the Ingress LoadBalancer IP:

```bash
# Get LoadBalancer IP
kubectl get ingress gymit-ingress -n gymit

# Add A record in your DNS:
# gymit.example.com -> <EXTERNAL-IP>
# www.gymit.example.com -> <EXTERNAL-IP>
```

### Step 5: Verify Deployment

```bash
# Check pod status
kubectl get pods -n gymit

# Check HPA status
kubectl get hpa -n gymit

# Check services
kubectl get svc -n gymit

# View logs
kubectl logs -f deployment/api-gateway -n gymit
```

## Monitoring and Scaling

### View Auto-Scaling Status

```bash
# Watch HPA in real-time
kubectl get hpa -n gymit -w

# Detailed HPA status
kubectl describe hpa api-gateway-hpa -n gymit
```

### Manual Scaling (if needed)

```bash
# Scale specific deployment
kubectl scale deployment api-gateway -n gymit --replicas=10

# Scale all deployments
kubectl scale deployment --all -n gymit --replicas=5
```

### Resource Usage

```bash
# View resource consumption
kubectl top pods -n gymit
kubectl top nodes
```

## Maintenance

### Update Application

```bash
# Build and push new image
docker build -t <your-registry>/gymit-api-gateway:v2.0.0 .
docker push <your-registry>/gymit-api-gateway:v2.0.0

# Update deployment
kubectl set image deployment/api-gateway api-gateway=<your-registry>/gymit-api-gateway:v2.0.0 -n gymit

# Check rollout status
kubectl rollout status deployment/api-gateway -n gymit

# Rollback if needed
kubectl rollout undo deployment/api-gateway -n gymit
```

### Database Backups

```bash
# Backup PostgreSQL databases
kubectl exec -it auth-db-0 -n gymit -- pg_dump -U authuser authdb > auth-db-backup.sql
kubectl exec -it user-db-0 -n gymit -- pg_dump -U useruser userdb > user-db-backup.sql
kubectl exec -it tournament-db-0 -n gymit -- pg_dump -U tournamentuser tournamentdb > tournament-db-backup.sql
```

### Update Secrets

```bash
# Update secrets without downtime
kubectl create secret generic gymit-secrets-new --from-literal=SECRET_KEY=<new-value> -n gymit
kubectl patch deployment api-gateway -n gymit -p '{"spec":{"template":{"spec":{"containers":[{"name":"api-gateway","envFrom":[{"secretRef":{"name":"gymit-secrets-new"}}]}]}}}}'
```

## Troubleshooting

### Pods not starting

```bash
# Check pod events
kubectl describe pod <pod-name> -n gymit

# View pod logs
kubectl logs <pod-name> -n gymit

# Check resource constraints
kubectl top pods -n gymit
kubectl describe nodes
```

### Database connection issues

```bash
# Test database connectivity
kubectl exec -it auth-service-xxx -n gymit -- ping auth-db
kubectl exec -it auth-service-xxx -n gymit -- nc -zv auth-db 5432
```

### HPA not scaling

```bash
# Check metrics server
kubectl top pods -n gymit

# Verify HPA configuration
kubectl describe hpa api-gateway-hpa -n gymit

# Check if metrics are available
kubectl get --raw /apis/metrics.k8s.io/v1beta1/pods
```

## Security Considerations

1. **Network Policies**: Enforced to limit pod-to-pod communication
2. **Secrets Management**: Use external secret management (Vault, AWS Secrets Manager)
3. **SSL/TLS**: Automatic certificate management via cert-manager
4. **Rate Limiting**: Configured at Ingress level
5. **RBAC**: Configure appropriate service accounts and roles

## Performance Optimization

1. **Connection Pooling**: Configured in database connections
2. **Redis Caching**: Shared cache for session management
3. **Resource Limits**: Set to prevent resource exhaustion
4. **Pod Disruption Budgets**: Ensure high availability during updates
5. **Anti-Affinity**: Spread replicas across nodes for resilience

## Cost Optimization

1. **Right-sizing**: Monitor actual usage and adjust resources
2. **Cluster Autoscaling**: Enable cluster autoscaler for node scaling
3. **Spot Instances**: Use for non-critical workloads
4. **Resource Requests**: Set accurately to avoid over-provisioning
5. **HPA Tuning**: Adjust scaling thresholds based on actual load

## License

See the main LICENSE file in the repository root.
