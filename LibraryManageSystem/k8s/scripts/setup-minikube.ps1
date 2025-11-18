# Setup Minikube for Library Management System
param(
    [string]$MinikubeProfile = "library-demo"
)

Write-Host "Setting up Minikube for Library Management System..." -ForegroundColor Green

# Start Minikube with required addons
minikube start --profile $MinikubeProfile --memory 4096 --cpus 2

# Enable necessary addons
minikube addons enable ingress --profile $MinikubeProfile
minikube addons enable metrics-server --profile $MinikubeProfile

# Set docker environment to Minikube's docker daemon
minikube docker-env --profile $MinikubeProfile | Invoke-Expression

Write-Host "Minikube setup complete. Profile: $MinikubeProfile" -ForegroundColor Green
Write-Host "Don't forget to build and push your Docker image to Minikube's registry." -ForegroundColor Yellow