# Deploy Library Management System to Kubernetes
param(
    [string]$Namespace = "library-system",
    [string]$MinikubeProfile = "library-demo"
)

Write-Host "Deploying Library Management System to Kubernetes..." -ForegroundColor Green

# Set kubectl context to Minikube
minikube kubectl -- config use-context $MinikubeProfile

# Create namespace
kubectl create namespace $Namespace --dry-run=client -o yaml | kubectl apply -f -

# Apply manifests in order
kubectl apply -f manifests/namespace.yaml
kubectl apply -f manifests/configmap.yaml
kubectl apply -f manifests/secret.yaml

# Deploy PostgreSQL
kubectl apply -f manifests/postgres/

# Deploy Redis
kubectl apply -f manifests/redis/

# Wait for databases to be ready
Write-Host "Waiting for PostgreSQL to be ready..." -ForegroundColor Yellow
kubectl wait --for=condition=ready pod -l app=library-postgres -n $Namespace --timeout=300s

Write-Host "Waiting for Redis to be ready..." -ForegroundColor Yellow
kubectl wait --for=condition=ready pod -l app=library-redis -n $Namespace --timeout=300s

# Deploy application
kubectl apply -f manifests/app/

# Deploy nginx
kubectl apply -f manifests/nginx/

# Deploy monitoring
kubectl apply -f manifests/monitoring/

# Deploy ingress
kubectl apply -f manifests/ingress.yaml

Write-Host "Deployment complete!" -ForegroundColor Green
Write-Host "Run .\port-forward.ps1 to access services locally." -ForegroundColor Cyan