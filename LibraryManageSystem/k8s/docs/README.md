# Kubernetes Deployment Guide

This directory contains Kubernetes manifests and scripts for deploying the Library Management System on Minikube.

## Prerequisites

- Minikube installed
- kubectl installed
- Docker installed
- PowerShell

## Quick Start

1. **Setup Minikube:**
   ```powershell
   .\scripts\setup-minikube.ps1
   ```

2. **Build and load Docker image:**
   ```powershell
   # In the project root
   docker build -t library-api:latest .
   minikube image load library-api:latest
   ```

3. **Deploy to Kubernetes:**
   ```powershell
   .\scripts\deploy.ps1
   ```

4. **Access the application:**
   ```powershell
   .\scripts\port-forward.ps1
   ```
   Then visit:
   - API: http://localhost:8000
   - Swagger: http://localhost:8000/swagger/
   - Grafana: http://localhost:3000 (admin/admin123)
   - Prometheus: http://localhost:9090

## Architecture

The deployment includes:
- **PostgreSQL**: Database with persistent storage
- **Redis**: Caching and rate limiting
- **Flask App**: Main application with 2 replicas
- **Nginx**: Reverse proxy and load balancer
- **Prometheus**: Monitoring and metrics collection
- **Grafana**: Dashboards and visualization
- **Exporters**: System and service metrics

## Configuration

- Environment variables are managed via ConfigMap and Secret
- Secrets are base64 encoded in `secret.yaml`
- Update the secrets before deployment

## Troubleshooting

- Check pod status: `kubectl get pods -n library-system`
- View logs: `kubectl logs -n library-system <pod-name>`
- Debug: `kubectl describe -n library-system <resource>`

## Cleanup

To remove all resources:
```powershell
.\scripts\undeploy.ps1
```