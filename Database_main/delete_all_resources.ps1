# PowerShell script to DELETE ALL Azure resources
# WARNING: This will permanently delete all resources in the resource group!
# Use this only if you want to completely remove everything and save all costs

Write-Host "========================================" -ForegroundColor Red
Write-Host "WARNING: DELETE ALL RESOURCES" -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Red
Write-Host ""
Write-Host "This script will PERMANENTLY DELETE all resources in resource group 'iot-project-rg'" -ForegroundColor Yellow
Write-Host "This includes:" -ForegroundColor Yellow
Write-Host "  - Service Bus Namespace" -ForegroundColor White
Write-Host "  - Function App" -ForegroundColor White
Write-Host "  - App Service Plan" -ForegroundColor White
Write-Host "  - Application Insights" -ForegroundColor White
Write-Host "  - MySQL Flexible Server" -ForegroundColor White
Write-Host "  - Storage Account" -ForegroundColor White
Write-Host "  - Container Registry" -ForegroundColor White
Write-Host "  - Container Instances" -ForegroundColor White
Write-Host "  - ALL DATA IN DATABASES" -ForegroundColor Red
Write-Host ""
Write-Host "This action CANNOT be undone!" -ForegroundColor Red
Write-Host ""

$confirm = Read-Host "Type 'DELETE' to confirm deletion"

if ($confirm -ne "DELETE") {
    Write-Host "Deletion cancelled." -ForegroundColor Green
    exit 0
}

$resourceGroup = "iot-project-rg"

# Check if resource group exists
Write-Host ""
Write-Host "Checking resource group..." -ForegroundColor Yellow
$rgExists = az group exists --name $resourceGroup --output tsv

if ($rgExists -eq "false") {
    Write-Host "Resource group '$resourceGroup' does not exist. Nothing to delete." -ForegroundColor Yellow
    exit 0
}

Write-Host "Deleting resource group '$resourceGroup' and ALL resources..." -ForegroundColor Red
Write-Host "This may take several minutes..." -ForegroundColor Yellow
Write-Host ""

# Delete entire resource group (this deletes everything)
az group delete --name $resourceGroup --yes --no-wait

Write-Host ""
Write-Host "Deletion initiated. Resources are being deleted in the background." -ForegroundColor Yellow
Write-Host "You can check the status in Azure Portal." -ForegroundColor Yellow
Write-Host ""
Write-Host "To verify deletion:" -ForegroundColor Cyan
Write-Host "  az group show --name $resourceGroup" -ForegroundColor Yellow
Write-Host ""

