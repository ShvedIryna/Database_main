$RESOURCE_GROUP = "iot-project-rg"
$LOCATION = "polandcentral"
$SERVICE_BUS_NAMESPACE = "iot-sensors-namespace"
$QUEUE_NAME = "sensor-data-queue"
$SQL_SERVER = "iot-sql-server"
$SQL_DB = "iot-sensors-db"
$SQL_ADMIN = "sqladmin"
$SQL_PASSWORD = "YourSecurePassword123!"
$FUNCTION_APP = "iot-sensors-processor"
$STORAGE_ACCOUNT = "iotfunctionsstorage"
$ACR_NAME = "iotsensorsacr"

Write-Host "=== Creating Resource Group ===" -ForegroundColor Green
az group create --name $RESOURCE_GROUP --location $LOCATION

Write-Host "`n=== Creating Service Bus ===" -ForegroundColor Green
az servicebus namespace create `
    --resource-group $RESOURCE_GROUP `
    --name $SERVICE_BUS_NAMESPACE `
    --location $LOCATION `
    --sku Standard

az servicebus queue create `
    --resource-group $RESOURCE_GROUP `
    --namespace-name $SERVICE_BUS_NAMESPACE `
    --name $QUEUE_NAME `
    --max-delivery-count 3 `
    --enable-dead-lettering-on-message-expiration true `
    --default-message-time-to-live P7D

Write-Host "`n=== Getting Service Bus Connection String ===" -ForegroundColor Green
$SERVICE_BUS_CONN = az servicebus namespace authorization-rule keys list `
    --resource-group $RESOURCE_GROUP `
    --namespace-name $SERVICE_BUS_NAMESPACE `
    --name RootManageSharedAccessKey `
    --query primaryConnectionString `
    --output tsv

Write-Host "Service Bus Connection String: $SERVICE_BUS_CONN" -ForegroundColor Yellow

Write-Host "`n=== Creating SQL Server ===" -ForegroundColor Green
az sql server create `
    --name $SQL_SERVER `
    --resource-group $RESOURCE_GROUP `
    --location $LOCATION `
    --admin-user $SQL_ADMIN `
    --admin-password $SQL_PASSWORD

az sql server firewall-rule create `
    --resource-group $RESOURCE_GROUP `
    --server $SQL_SERVER `
    --name AllowAzureServices `
    --start-ip-address 0.0.0.0 `
    --end-ip-address 0.0.0.0

Write-Host "`n=== Creating SQL Database ===" -ForegroundColor Green
az sql db create `
    --resource-group $RESOURCE_GROUP `
    --server $SQL_SERVER `
    --name $SQL_DB `
    --service-objective Basic `
    --backup-storage-redundancy Local

$SQL_CONN_STRING = "Server=tcp:$SQL_SERVER.database.windows.net,1433;Initial Catalog=$SQL_DB;Persist Security Info=False;User ID=$SQL_ADMIN;Password=$SQL_PASSWORD;MultipleActiveResultSets=False;Encrypt=True;TrustServerCertificate=False;Connection Timeout=30;"

Write-Host "`n=== Creating Storage Account ===" -ForegroundColor Green
az storage account create `
    --name $STORAGE_ACCOUNT `
    --resource-group $RESOURCE_GROUP `
    --location $LOCATION `
    --sku Standard_LRS

Write-Host "`n=== Creating Function App ===" -ForegroundColor Green
az functionapp create `
    --resource-group $RESOURCE_GROUP `
    --consumption-plan-location $LOCATION `
    --runtime python `
    --runtime-version 3.10 `
    --functions-version 4 `
    --name $FUNCTION_APP `
    --storage-account $STORAGE_ACCOUNT `
    --os-type Linux

Write-Host "`n=== Configuring Function App Settings ===" -ForegroundColor Green
az functionapp config appsettings set `
    --name $FUNCTION_APP `
    --resource-group $RESOURCE_GROUP `
    --settings `
        "ServiceBusConnection=$SERVICE_BUS_CONN" `
        "SqlConnectionString=$SQL_CONN_STRING" `
        "FUNCTIONS_WORKER_RUNTIME=python"

Write-Host "`n=== Creating Container Registry ===" -ForegroundColor Green
az acr create `
    --resource-group $RESOURCE_GROUP `
    --name $ACR_NAME `
    --sku Basic

Write-Host "`n=== Configuring ACR Admin ===" -ForegroundColor Green
az acr update --name $ACR_NAME --admin-enabled true
$ACR_PASSWORD = az acr credential show --name $ACR_NAME --query "passwords[0].value" --output tsv
$ACR_USERNAME = $ACR_NAME

Write-Host "`n=== Configuration Information ===" -ForegroundColor Cyan
Write-Host "Service Bus Connection: $SERVICE_BUS_CONN" -ForegroundColor Yellow
Write-Host "SQL Connection String: $SQL_CONN_STRING" -ForegroundColor Yellow
Write-Host "ACR Login Server: $ACR_NAME.azurecr.io" -ForegroundColor Yellow
Write-Host "ACR Username: $ACR_USERNAME" -ForegroundColor Yellow
Write-Host "ACR Password: $ACR_PASSWORD" -ForegroundColor Yellow

Write-Host "`n=== Next Steps ===" -ForegroundColor Green
Write-Host "1. Update iot_config.json with Service Bus Connection String"
Write-Host "2. Execute SQL script database_schema.sql on SQL Database"
Write-Host "3. Deploy Azure Functions: cd iot_functions && func azure functionapp publish $FUNCTION_APP"
Write-Host "4. Build Docker image: az acr build --registry $ACR_NAME --image sensor-emulator:latest ."
$containerCmd = "az container create --resource-group $RESOURCE_GROUP --name sensor-emulator --image $ACR_NAME.azurecr.io/sensor-emulator:latest --registry-login-server $ACR_NAME.azurecr.io --registry-username $ACR_USERNAME --registry-password $ACR_PASSWORD --environment-variables SERVICE_BUS_CONNECTION_STRING=`"$SERVICE_BUS_CONN`" QUEUE_NAME=`"$QUEUE_NAME`""
Write-Host "5. Run container: $containerCmd"


