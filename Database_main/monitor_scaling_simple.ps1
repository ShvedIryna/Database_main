# Простий скрипт моніторингу масштабування для Windows PowerShell

$CONTAINER_APP_NAME = "db-repo-app"
$RESOURCE_GROUP = "your-resource-group"
$INTERVAL = 10  # секунди між перевірками

Write-Host "=========================================="
Write-Host "Monitoring Container App Scaling"
Write-Host "=========================================="
Write-Host "Container App: $CONTAINER_APP_NAME"
Write-Host "Resource Group: $RESOURCE_GROUP"
Write-Host "Update interval: $INTERVAL seconds"
Write-Host "Press Ctrl+C to stop"
Write-Host "=========================================="
Write-Host ""

while ($true) {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    
    # Отримати кількість реплік
    $replicas = az containerapp replica list --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP --query "[].{name:name, status:properties.runningState}" -o json | ConvertFrom-Json
    $replicaCount = $replicas.Count
    
    # Отримати налаштування масштабування
    $scaleConfig = az containerapp show --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP --query "properties.template.scale" -o json | ConvertFrom-Json
    $minReplicas = $scaleConfig.minReplicas
    $maxReplicas = $scaleConfig.maxReplicas
    
    # Отримати метрики CPU та Memory
    $subscriptionId = az account show --query id -o tsv
    $resourceId = "/subscriptions/$subscriptionId/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.App/containerApps/$CONTAINER_APP_NAME"
    $endTime = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    $startTime = (Get-Date).AddMinutes(-5).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    
    try {
        $cpuMetrics = az monitor metrics list --resource $resourceId --metric "CpuPercentage" --start-time $startTime --end-time $endTime --interval PT1M --query "value[0].timeseries[0].data[-1].average" -o tsv
        $memoryMetrics = az monitor metrics list --resource $resourceId --metric "MemoryPercentage" --start-time $startTime --end-time $endTime --interval PT1M --query "value[0].timeseries[0].data[-1].average" -o tsv
        
        $cpuValue = if ($cpuMetrics) { [math]::Round([double]$cpuMetrics, 2) } else { "N/A" }
        $memoryValue = if ($memoryMetrics) { [math]::Round([double]$memoryMetrics, 2) } else { "N/A" }
    } catch {
        $cpuValue = "Error"
        $memoryValue = "Error"
    }
    
    # Вивести інформацію
    Write-Host "[$timestamp]"
    Write-Host "  Replicas: $replicaCount (min: $minReplicas, max: $maxReplicas)"
    Write-Host "  CPU: $cpuValue%"
    Write-Host "  Memory: $memoryValue%"
    Write-Host ""
    
    Start-Sleep -Seconds $INTERVAL
}

