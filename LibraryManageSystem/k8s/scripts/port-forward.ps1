# Port forward services for local access
param(
    [string]$Namespace = "library-system"
)

Write-Host "Setting up port forwarding for local access..." -ForegroundColor Green

# Port forward services in background
Start-Job -ScriptBlock {
    kubectl port-forward -n $using:Namespace svc/library-nginx 8080:80
} -Name "nginx-forward"

Start-Job -ScriptBlock {
    kubectl port-forward -n $using:Namespace svc/library-app 8000:8000
} -Name "app-forward"

Start-Job -ScriptBlock {
    kubectl port-forward -n $using:Namespace svc/library-grafana 3000:3000
} -Name "grafana-forward"

Start-Job -ScriptBlock {
    kubectl port-forward -n $using:Namespace svc/library-prometheus 9090:9090
} -Name "prometheus-forward"

Write-Host "Port forwarding active:" -ForegroundColor Cyan
Write-Host "  - Nginx: http://localhost:8080" -ForegroundColor White
Write-Host "  - API: http://localhost:8000" -ForegroundColor White
Write-Host "  - Grafana: http://localhost:3000" -ForegroundColor White
Write-Host "  - Prometheus: http://localhost:9090" -ForegroundColor White
Write-Host "Press Ctrl+C to stop forwarding." -ForegroundColor Yellow

# Keep script running
try {
    while ($true) {
        Start-Sleep -Seconds 1
    }
} finally {
    # Cleanup jobs on exit
    Get-Job | Stop-Job
    Get-Job | Remove-Job
}