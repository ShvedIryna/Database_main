# PowerShell script to stop all Azure services to save budget
# This script stops/pauses all resources created for the IoT project

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Stopping Azure IoT Services" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$resourceGroup = "iot-project-rg"

# Check if resource group exists
Write-Host "Checking resource group..." -ForegroundColor Yellow
$rgExists = az group exists --name $resourceGroup --output tsv

if ($rgExists -eq "false") {
    Write-Host "Resource group '$resourceGroup' does not exist. Nothing to stop." -ForegroundColor Yellow
    exit 0
}

Write-Host "Resource group found: $resourceGroup" -ForegroundColor Green
Write-Host ""

# 1. Stop/Delete Container Instance (saves compute costs)
Write-Host "1. Stopping Container Instance..." -ForegroundColor Yellow
try {
    az container stop --resource-group $resourceGroup --name sensor-emulator-container 2>$null
    Write-Host "   Container Instance stopped" -ForegroundColor Green
} catch {
    Write-Host "   Container Instance not found or already stopped" -ForegroundColor Yellow
}

# Alternative: Delete container instance completely
Write-Host "   Deleting Container Instance to save costs..." -ForegroundColor Yellow
az container delete --resource-group $resourceGroup --name sensor-emulator-container --yes 2>$null
Write-Host "   Container Instance deleted" -ForegroundColor Green
Write-Host ""

# 2. Pause MySQL Flexible Server (saves database costs)
Write-Host "2. Pausing MySQL Flexible Server..." -ForegroundColor Yellow
try {
    az mysql flexible-server stop --resource-group $resourceGroup --name iot-sql-flexible-server 2>$null
    Write-Host "   MySQL Flexible Server paused" -ForegroundColor Green
} catch {
    Write-Host "   MySQL Flexible Server not found or already paused" -ForegroundColor Yellow
}
Write-Host ""

# 3. Stop Function App (saves compute costs)
Write-Host "3. Stopping Function App..." -ForegroundColor Yellow
try {
    az functionapp stop --resource-group $resourceGroup --name iot-sensors-processor 2>$null
    Write-Host "   Function App stopped" -ForegroundColor Green
} catch {
    Write-Host "   Function App not found or already stopped" -ForegroundColor Yellow
}
Write-Host ""

# 4. Stop App Service Plan (saves compute costs)
Write-Host "4. Stopping App Service Plan..." -ForegroundColor Yellow
try {
    az appservice plan stop --resource-group $resourceGroup --name iot-functions-plan 2>$null
    Write-Host "   App Service Plan stopped" -ForegroundColor Green
} catch {
    Write-Host "   App Service Plan not found or already stopped" -ForegroundColor Yellow
}
Write-Host ""

# 5. Optional: Delete Container Registry (saves storage costs)
Write-Host "5. Deleting Container Registry (optional - saves storage costs)..." -ForegroundColor Yellow
$deleteACR = Read-Host "   Delete Container Registry? (y/N)"
if ($deleteACR -eq "y" -or $deleteACR -eq "Y") {
    try {
        az acr delete --resource-group $resourceGroup --name iotsensorsacr --yes 2>$null
        Write-Host "   Container Registry deleted" -ForegroundColor Green
    } catch {
        Write-Host "   Container Registry not found or already deleted" -ForegroundColor Yellow
    }
} else {
    Write-Host "   Container Registry kept" -ForegroundColor Yellow
}
Write-Host ""

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Stopped services:" -ForegroundColor Green
Write-Host "  - Container Instance (deleted)" -ForegroundColor White
Write-Host "  - MySQL Flexible Server (paused)" -ForegroundColor White
Write-Host "  - Function App (stopped)" -ForegroundColor White
Write-Host "  - App Service Plan (stopped)" -ForegroundColor White
Write-Host ""
Write-Host "Services still running (minimal cost):" -ForegroundColor Yellow
Write-Host "  - Service Bus Namespace (Standard tier - minimal cost)" -ForegroundColor White
Write-Host "  - Storage Account (pay-per-use, minimal if empty)" -ForegroundColor White
Write-Host "  - Application Insights (pay-per-use, minimal if no data)" -ForegroundColor White
Write-Host ""
Write-Host "To completely remove all resources, run:" -ForegroundColor Cyan
Write-Host "  az group delete --name $resourceGroup --yes --no-wait" -ForegroundColor Yellow
Write-Host ""
Write-Host "To restart services later:" -ForegroundColor Cyan
Write-Host "  - MySQL: az mysql flexible-server start --resource-group $resourceGroup --name iot-sql-flexible-server" -ForegroundColor Yellow
Write-Host "  - Function App: az functionapp start --resource-group $resourceGroup --name iot-sensors-processor" -ForegroundColor Yellow
Write-Host ""

