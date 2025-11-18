# Undeploy Library Management System from Kubernetes
param(
    [string]$Namespace = "library-system"
)

Write-Host "Undeploying Library Management System from Kubernetes..." -ForegroundColor Yellow

# Delete all resources
kubectl delete -f manifests/ingress.yaml
kubectl delete -f manifests/monitoring/
kubectl delete -f manifests/nginx/
kubectl delete -f manifests/app/
kubectl delete -f manifests/redis/
kubectl delete -f manifests/postgres/
kubectl delete -f manifests/secret.yaml
kubectl delete -f manifests/configmap.yaml
kubectl delete -f manifests/namespace.yaml

Write-Host "Undeployment complete!" -ForegroundColor Green