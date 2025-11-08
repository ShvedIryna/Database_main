$RESOURCE_GROUP = "your-resource-group"
$CONTAINER_APP_NAME = "db-repo-app"
$MONITOR_INTERVAL = 10
$LOG_FILE = "scaling_monitor.log"

function Write-Log {
    param([string]$Message, [string]$Color = "Green")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $colorMap = @{
        "Green" = "Green"
        "Yellow" = "Yellow"
        "Red" = "Red"
        "Blue" = "Cyan"
    }
    Write-Host "[$timestamp] [INFO] $Message" -ForegroundColor $colorMap[$Color]
}

function Write-LogToFile {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "[$timestamp] $Message" | Out-File -FilePath $LOG_FILE -Append
}

function Get-ReplicaCount {
    try {
        $replicas = az containerapp replica list --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP --query "[].{name:name, status:properties.runningState}" -o json 2>$null | ConvertFrom-Json
        $runningCount = ($replicas | Where-Object { $_.status -eq "Running" }).Count
        $totalCount = $replicas.Count
        
        $appInfo = az containerapp show --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP --query "{minReplicas:properties.template.scale.minReplicas, maxReplicas:properties.template.scale.maxReplicas}" -o json 2>$null | ConvertFrom-Json
        
        return @{
            Running = if ($runningCount) { $runningCount } else { 0 }
            Total = if ($totalCount) { $totalCount } else { 0 }
            Min = $appInfo.minReplicas
            Max = $appInfo.maxReplicas
        }
    } catch {
        return @{ Running = 0; Total = 0; Min = 1; Max = 10 }
    }
}

function Get-Metrics {
    try {
        $subscriptionId = az account show --query id -o tsv 2>$null
        $resourceId = "/subscriptions/$subscriptionId/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.App/containerApps/$CONTAINER_APP_NAME"
        
        $endTime = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
        $startTime = (Get-Date).AddMinutes(-5).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
        
        $cpuMetrics = az monitor metrics list --resource $resourceId --metric "CpuPercentage" --start-time $startTime --end-time $endTime --interval PT1M --query "value[0].timeseries[0].data[-1].average" -o tsv 2>$null
        $memoryMetrics = az monitor metrics list --resource $resourceId --metric "MemoryPercentage" --start-time $startTime --end-time $endTime --interval PT1M --query "value[0].timeseries[0].data[-1].average" -o tsv 2>$null
        
        return @{
            CPU = if ($cpuMetrics -and $cpuMetrics -ne "null") { [double]$cpuMetrics } else { $null }
            Memory = if ($memoryMetrics -and $memoryMetrics -ne "null") { [double]$memoryMetrics } else { $null }
        }
    } catch {
        return @{ CPU = $null; Memory = $null }
    }
}

Write-Log "Starting monitoring for Container App: $CONTAINER_APP_NAME" "Green"
Write-Log "Resource Group: $RESOURCE_GROUP" "Green"
Write-Log "Monitoring interval: $MONITOR_INTERVAL seconds" "Green"
Write-Log "Log file: $LOG_FILE" "Green"
Write-Host ""
Write-LogToFile "=== Monitoring started ==="

try {
    while ($true) {
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        
        $replicaInfo = Get-ReplicaCount
        $metrics = Get-Metrics
        
        Write-Host "==========================================" -ForegroundColor Cyan
        Write-Host "[MONITOR] Time: $timestamp" -ForegroundColor Cyan
        Write-Host "[MONITOR] Replica count: $($replicaInfo.Running) (min: $($replicaInfo.Min), max: $($replicaInfo.Max))" -ForegroundColor Cyan
        
        if ($metrics.CPU -ne $null) {
            Write-Host "CPU usage: $($metrics.CPU.ToString('F2'))%" -ForegroundColor Yellow
            Write-LogToFile "CPU: $($metrics.CPU)%, Replicas: $($replicaInfo.Running)"
        } else {
            Write-Host "CPU usage: N/A" -ForegroundColor Gray
        }
        
        if ($metrics.Memory -ne $null) {
            Write-Host "Memory usage: $($metrics.Memory.ToString('F2'))%" -ForegroundColor Yellow
            Write-LogToFile "Memory: $($metrics.Memory)%, Replicas: $($replicaInfo.Running)"
        } else {
            Write-Host "Memory usage: N/A" -ForegroundColor Gray
        }
        
        Write-Host "==========================================" -ForegroundColor Cyan
        Write-Host ""
        
        Start-Sleep -Seconds $MONITOR_INTERVAL
    }
} catch {
    Write-Log "Monitoring stopped" "Red"
    Write-LogToFile "=== Monitoring stopped ==="
}
