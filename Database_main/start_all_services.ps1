# PowerShell script to start all Azure services
# This script starts/resumes all resources for the IoT project

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Azure IoT Services" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$resourceGroup = "iot-project-rg"

# Check if resource group exists
Write-Host "Checking resource group..." -ForegroundColor Yellow
$rgExists = az group exists --name $resourceGroup --output tsv

if ($rgExists -eq "false") {
    Write-Host "Resource group '$resourceGroup' does not exist." -ForegroundColor Red
    Write-Host "Please run azure_iot_setup.ps1 first to create resources." -ForegroundColor Yellow
    exit 1
}

Write-Host "Resource group found: $resourceGroup" -ForegroundColor Green
Write-Host ""

# 1. Start MySQL Flexible Server
Write-Host "1. Starting MySQL Flexible Server..." -ForegroundColor Yellow
try {
    az mysql flexible-server start --resource-group $resourceGroup --name iot-sql-flexible-server
    Write-Host "   MySQL Flexible Server started" -ForegroundColor Green
} catch {
    Write-Host "   Error starting MySQL Flexible Server: $_" -ForegroundColor Red
}
Write-Host ""

# 2. Start App Service Plan
Write-Host "2. Starting App Service Plan..." -ForegroundColor Yellow
try {
    az appservice plan start --resource-group $resourceGroup --name iot-functions-plan
    Write-Host "   App Service Plan started" -ForegroundColor Green
} catch {
    Write-Host "   Error starting App Service Plan: $_" -ForegroundColor Red
}
Write-Host ""

# 3. Start Function App
Write-Host "3. Starting Function App..." -ForegroundColor Yellow
try {
    az functionapp start --resource-group $resourceGroup --name iot-sensors-processor
    Write-Host "   Function App started" -ForegroundColor Green
} catch {
    Write-Host "   Error starting Function App: $_" -ForegroundColor Red
}
Write-Host ""

# 4. Recreate Container Instance (if needed)
Write-Host "4. Container Instance..." -ForegroundColor Yellow
Write-Host "   Note: Container Instance was deleted to save costs." -ForegroundColor Yellow
Write-Host "   To recreate it, run the container creation command from IOT_COMPLETE_GUIDE.md" -ForegroundColor Yellow
Write-Host ""

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Started services:" -ForegroundColor Green
Write-Host "  - MySQL Flexible Server" -ForegroundColor White
Write-Host "  - App Service Plan" -ForegroundColor White
Write-Host "  - Function App" -ForegroundColor White
Write-Host ""
Write-Host "Services that need manual recreation:" -ForegroundColor Yellow
Write-Host "  - Container Instance (run container creation command)" -ForegroundColor White
Write-Host ""
Write-Host "Wait a few minutes for services to fully start before using them." -ForegroundColor Cyan
Write-Host ""

