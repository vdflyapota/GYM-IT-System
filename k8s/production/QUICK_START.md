# Quick Start Guide - Kubernetes Deployment

## 🚀 Deploy in 5 Minutes

### Prerequisites Check
```bash
# Verify kubectl is installed and connected
kubectl version --short
kubectl cluster-info

# Verify you have a cluster with sufficient resources
kubectl get nodes
```

### Step 1: Clone and Navigate
```bash
cd k8s/production
```

### Step 2: Update Secrets (CRITICAL!)
```bash
# Generate secure keys
export SECRET_KEY=$(openssl rand -hex 32)
export JWT_SECRET_KEY=$(openssl rand -hex 32)

# Update secrets file
sed -i "s/change-this-to-a-random-secret-key-in-production/$SECRET_KEY/g" 02-secrets.yaml
sed -i "s/change-this-to-a-random-jwt-secret-in-production/$JWT_SECRET_KEY/g" 02-secrets.yaml
```

### Step 3: Update Domain (if you have one)
```bash
# Replace gymit.example.com with your domain in 09-ingress.yaml
sed -i "s/gymit.example.com/yourdomain.com/g" 09-ingress.yaml
```

### Step 4: Deploy Everything
```bash
./deploy.sh
```

That's it! The script will:
- Create namespace
- Deploy databases
- Deploy all microservices
- Configure autoscaling
- Setup ingress
- Apply security policies

### Step 5: Verify Deployment
```bash
# Check all pods are running
kubectl get pods -n gymit

# Watch autoscaling
kubectl get hpa -n gymit -w

# Get Ingress IP
kubectl get ingress -n gymit
```

### Step 6: Access Application
```bash
# Get LoadBalancer IP
INGRESS_IP=$(kubectl get ingress gymit-ingress -n gymit -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo "Access application at: http://$INGRESS_IP"

# Or with domain (after DNS setup)
echo "Access application at: https://yourdomain.com"
```

## 📊 Monitor Your Deployment

### Real-time Pod Status
```bash
watch kubectl get pods -n gymit
```

### View Logs
```bash
# API Gateway logs
kubectl logs -f deployment/api-gateway -n gymit

# All services
kubectl logs -f -l tier=backend -n gymit --max-log-requests=10
```

### Resource Usage
```bash
kubectl top pods -n gymit
kubectl top nodes
```

### Scaling Status
```bash
kubectl get hpa -n gymit
```

## 🔧 Common Tasks

### Scale a Service Manually
```bash
kubectl scale deployment api-gateway -n gymit --replicas=10
```

### Update an Application
```bash
# Update image
kubectl set image deployment/api-gateway api-gateway=myregistry/api-gateway:v2.0 -n gymit

# Watch rollout
kubectl rollout status deployment/api-gateway -n gymit
```

### Rollback
```bash
kubectl rollout undo deployment/api-gateway -n gymit
```

### Delete Everything
```bash
kubectl delete namespace gymit
```

## 🐛 Troubleshooting

### Pods not starting?
```bash
kubectl describe pod <pod-name> -n gymit
kubectl logs <pod-name> -n gymit
```

### Database connection issues?
```bash
# Check database is ready
kubectl get pods -l app=auth-db -n gymit

# Test connection
kubectl exec -it <service-pod> -n gymit -- nc -zv auth-db 5432
```

### HPA not scaling?
```bash
# Check metrics server
kubectl top pods -n gymit

# If empty, install metrics server:
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

## 📈 Performance Testing

### Load Test with Apache Bench
```bash
# Install ab (Apache Bench)
sudo apt-get install apache2-utils

# Test API endpoint
ab -n 1000 -c 100 http://$INGRESS_IP/api/healthz

# Watch autoscaling in action
kubectl get hpa -n gymit -w
```

### Verify 5x Scalability
```bash
# Before load test
kubectl get hpa -n gymit

# During load test (in another terminal)
# Watch replicas increase automatically

# After load test
# Watch replicas decrease back to minimum
```

## 🔐 Security Checklist

- [ ] Updated secrets with random values
- [ ] Configured SSL/TLS certificates
- [ ] Set up network policies
- [ ] Configured RBAC (if needed)
- [ ] Enabled pod security policies
- [ ] Configured resource quotas
- [ ] Set up monitoring and alerts

## 📚 Next Steps

1. **Configure Monitoring**: Set up Prometheus and Grafana
2. **Configure Logging**: Set up ELK or Loki stack
3. **Backup Strategy**: Configure database backups
4. **CI/CD Integration**: Automate deployments
5. **Load Testing**: Validate 5x scalability
6. **Disaster Recovery**: Test restore procedures

## 🎯 Expected Results

After deployment, you should have:
- ✅ All pods running and healthy
- ✅ Auto-scaling configured (5x growth capacity)
- ✅ Ingress accessible
- ✅ Network policies enforced
- ✅ Databases persistent and backed up
- ✅ SSL/TLS certificates (if configured)

Happy deploying! 🚀
