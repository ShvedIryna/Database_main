$RESOURCE_GROUP = "your-resource-group"
$LOCATION = "polandcentral"
$ACR_NAME = "your-acr-name"
$CONTAINER_APP_NAME = "db-repo-app"
$CONTAINER_APP_ENV = "db-repo-env"
$IMAGE_NAME = "flask-rest-api"
$IMAGE_TAG = "latest"
$DB_HOST = "your-db-server.mysql.database.azure.com"
$DB_USER = "your_username"
$DB_PASSWORD = "your_password"
$DB_NAME = "your_database_name"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "FIX AND REDEPLOY" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""


Write-Host "0. Checking Resource Group..." -ForegroundColor Yellow
$rgExists = az group show --name $RESOURCE_GROUP --query name -o tsv 2>&1

if (-not $rgExists -or $rgExists -ne $RESOURCE_GROUP) {
    Write-Host "   Resource Group not found. Creating Resource Group..." -ForegroundColor Yellow
    az group create --name $RESOURCE_GROUP --location $LOCATION
    if ($LASTEXITCODE -ne 0) {
        Write-Host "   ERROR: Failed to create Resource Group" -ForegroundColor Red
        exit 1
    }
    Write-Host "   Resource Group created successfully." -ForegroundColor Green
} else {
    Write-Host "   Resource Group found." -ForegroundColor Green
}

Write-Host ""


Write-Host "1. Checking if Container App exists..." -ForegroundColor Yellow
$appExists = az containerapp show --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP --query name -o tsv 2>&1

if ($appExists -and $appExists -eq $CONTAINER_APP_NAME) {
    Write-Host "   Container App found. Checking logs..." -ForegroundColor Yellow
    $logsResult = az containerapp logs show --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP --tail 30 2>&1
    if ($LASTEXITCODE -ne 0 -and $logsResult -match "Could not find a revision") {
        Write-Host "   No active revisions found (app may be in failed state)" -ForegroundColor Yellow
    } else {
        Write-Host $logsResult
    }
    Write-Host ""
    Write-Host "2. Deleting old Container App..." -ForegroundColor Yellow
    az containerapp delete --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP --yes 2>&1 | Out-Null
    Write-Host "   Container App deleted." -ForegroundColor Green
} else {
    Write-Host "   Container App not found. Skipping deletion." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "2. Skipping deletion (Container App does not exist)..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "3. Checking Azure Container Registry..." -ForegroundColor Yellow
$acrListOutput = az acr list --query "[?name=='$ACR_NAME'].{name:name, rg:resourceGroup, location:location}" -o json 2>&1
$acrFound = $false
$acrRG = $RESOURCE_GROUP

try {
    $acrInAll = $acrListOutput | ConvertFrom-Json
    if ($acrInAll -and $acrInAll.Count -gt 0) {
        $acrRG = $acrInAll[0].rg
        $acrLocation = $acrInAll[0].location
        Write-Host "   Found ACR in resource group: $acrRG" -ForegroundColor Green
        Write-Host "   ACR location: $acrLocation" -ForegroundColor Green
        $LOCATION = $acrLocation
        $acrFound = $true
        Write-Host "   Using ACR location: $LOCATION" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ACR not found in any resource group" -ForegroundColor Yellow
    $acrFound = $false
}

if (-not $acrFound) {
    Write-Host "   ACR not found. Creating ACR..." -ForegroundColor Yellow
    Write-Host "   WARNING: If creation fails due to region policy, try:" -ForegroundColor Yellow
    Write-Host "   1. Create ACR manually via Azure Portal" -ForegroundColor White
    Write-Host "   2. Or use Docker Hub instead (see SOLUTION_ACR_ISSUE.md)" -ForegroundColor White
    Write-Host ""
    
    $acrCreated = $false
    
    $result = az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic --admin-enabled true --location $LOCATION 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        $acrCreated = $true
        Write-Host "   ACR created successfully in region: $LOCATION" -ForegroundColor Green
    } else {
        if ($result -match "RequestDisallowedByAzure" -or $result -match "region") {
            Write-Host "   ERROR: Region policy restriction. Your subscription may not allow ACR in this region." -ForegroundColor Red
            Write-Host "   SOLUTION: Create ACR manually via Azure Portal or use Docker Hub" -ForegroundColor Yellow
            Write-Host "   See SOLUTION_ACR_ISSUE.md for alternatives" -ForegroundColor Yellow
            Write-Host ""
            Write-Host "   Trying other regions anyway..." -ForegroundColor Yellow
        }
        
        $altLocations = @("polandcentral", "eastus", "westus2", "westeurope", "centralus", "southcentralus", "uksouth")
        
        foreach ($altLoc in $altLocations) {
            Write-Host "   Trying region: $altLoc" -ForegroundColor Yellow
            $result = az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic --admin-enabled true --location $altLoc 2>&1
            if ($LASTEXITCODE -eq 0) {
                $acrCreated = $true
                $LOCATION = $altLoc
                Write-Host "   ACR created successfully in region: $LOCATION" -ForegroundColor Green
                break
            }
        }
        
        if ($acrCreated -eq $false) {
            Write-Host ""
            Write-Host "   ==========================================" -ForegroundColor Red
            Write-Host "   FAILED TO CREATE ACR" -ForegroundColor Red
            Write-Host "   ==========================================" -ForegroundColor Red
            Write-Host "   Your Azure for Students subscription has region restrictions." -ForegroundColor Yellow
            Write-Host ""
            Write-Host "   OPTIONS:" -ForegroundColor Cyan
            Write-Host "   1. Create ACR manually via Azure Portal (often works when CLI doesn't)" -ForegroundColor White
            Write-Host "   2. Use Docker Hub instead - see SOLUTION_ACR_ISSUE.md" -ForegroundColor White
            Write-Host "   3. Contact Azure Support to enable more regions" -ForegroundColor White
            Write-Host ""
            Write-Host "   After creating ACR manually, run this script again." -ForegroundColor Yellow
            exit 1
        }
    }
} else {
    Write-Host "   ACR found." -ForegroundColor Green
    $acrFound = $true
    if ($acrInAll -and $acrInAll.Count -gt 0) {
        $acrLocation = $acrInAll[0].location
        $acrRG = $acrInAll[0].rg
        $LOCATION = $acrLocation
        Write-Host "   Using ACR location: $LOCATION" -ForegroundColor Yellow
        Write-Host "   Using ACR resource group: $acrRG" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "4. Logging into ACR..." -ForegroundColor Yellow
if ($acrFound) {
    Write-Host "   Logging into ACR: $ACR_NAME" -ForegroundColor Yellow
    $loginOutput = az acr login --name $ACR_NAME 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "   WARNING: ACR login failed (exit code: $LASTEXITCODE)" -ForegroundColor Yellow
        Write-Host "   Output: $loginOutput" -ForegroundColor Gray
        Write-Host "   This may be OK - Docker push will handle authentication" -ForegroundColor Yellow
        Write-Host "   Continuing with build and push..." -ForegroundColor Yellow
    } else {
        Write-Host "   Login successful" -ForegroundColor Green
    }
} else {
    Write-Host "   ERROR: ACR not found. Cannot proceed without ACR." -ForegroundColor Red
    Write-Host "   Please create ACR manually via Azure Portal in region 'Poland Central' or 'polandcentral'" -ForegroundColor Yellow
    Write-Host "   Then run this script again." -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "5. Rebuilding Docker image..." -ForegroundColor Yellow
$fullImageName = $ACR_NAME + ".azurecr.io/" + $IMAGE_NAME + ":" + $IMAGE_TAG
Write-Host "   Building image: $fullImageName" -ForegroundColor Yellow
docker build --platform linux/amd64 -t $fullImageName .
if ($LASTEXITCODE -ne 0) {
    Write-Host "   ERROR: Docker build failed" -ForegroundColor Red
    exit 1
}
Write-Host "   Pushing image to ACR..." -ForegroundColor Yellow
docker push $fullImageName
if ($LASTEXITCODE -ne 0) {
    Write-Host "   ERROR: Docker push failed. Trying to login again..." -ForegroundColor Yellow
    az acr login --name $ACR_NAME 2>&1 | Out-Null
    docker push $fullImageName
    if ($LASTEXITCODE -ne 0) {
        Write-Host "   ERROR: Docker push failed after retry" -ForegroundColor Red
        exit 1
    }
}
Write-Host "   Image pushed successfully" -ForegroundColor Green

Write-Host ""
Write-Host "6. Enabling admin user for ACR (if needed)..." -ForegroundColor Yellow
az acr update --name $ACR_NAME --admin-enabled true 2>&1 | Out-Null

Write-Host ""
Write-Host "7. Getting ACR credentials..." -ForegroundColor Yellow
if (-not $acrFound) {
    Write-Host "   ERROR: ACR not found. Cannot get credentials." -ForegroundColor Red
    exit 1
}

Write-Host "   Enabling admin user for ACR..." -ForegroundColor Yellow
az acr update --name $ACR_NAME --admin-enabled true 2>&1 | Out-Null
Start-Sleep -Seconds 3

Write-Host "   Retrieving credentials..." -ForegroundColor Yellow
$credsOutput = az acr credential show --name $ACR_NAME -o json 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "   ERROR: Cannot retrieve ACR credentials. Exit code: $LASTEXITCODE" -ForegroundColor Red
    Write-Host "   Output: $credsOutput" -ForegroundColor Yellow
    Write-Host "   Trying to enable admin user again..." -ForegroundColor Yellow
    az acr update --name $ACR_NAME --admin-enabled true 2>&1 | Out-Null
    Start-Sleep -Seconds 5
    $credsOutput = az acr credential show --name $ACR_NAME -o json 2>&1
}

if ($LASTEXITCODE -ne 0 -or $credsOutput -match "error" -or $credsOutput -match "ResourceNotFound") {
    Write-Host "   ERROR: Cannot retrieve ACR credentials after retry." -ForegroundColor Red
    Write-Host "   Output: $credsOutput" -ForegroundColor Yellow
    Write-Host "   Please check ACR exists: az acr list --query '[?name==''$ACR_NAME'']'" -ForegroundColor Yellow
    exit 1
}

try {
    $credsObj = $credsOutput | ConvertFrom-Json
    if ($credsObj -and $credsObj.passwords -and $credsObj.passwords.Count -gt 0) {
        $ACR_USERNAME = $credsObj.username
        $ACR_PASSWORD = $credsObj.passwords[0].value
        
        if ([string]::IsNullOrEmpty($ACR_USERNAME) -or [string]::IsNullOrEmpty($ACR_PASSWORD)) {
            Write-Host "   ERROR: Failed to get ACR credentials (empty values)" -ForegroundColor Red
            Write-Host "   Username: $ACR_USERNAME" -ForegroundColor Yellow
            Write-Host "   Password length: $($ACR_PASSWORD.Length)" -ForegroundColor Yellow
            exit 1
        }
        Write-Host "   ACR credentials retrieved successfully" -ForegroundColor Green
    } else {
        Write-Host "   ERROR: Failed to parse ACR credentials - invalid structure" -ForegroundColor Red
        Write-Host "   Output structure: $($credsObj | ConvertTo-Json -Depth 3)" -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "   ERROR: Failed to parse ACR credentials: $_" -ForegroundColor Red
    Write-Host "   Raw output: $credsOutput" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "8. Checking Container Apps Environment..." -ForegroundColor Yellow
$envExists = az containerapp env show --name $CONTAINER_APP_ENV --resource-group $RESOURCE_GROUP --query name -o tsv 2>&1

if (-not $envExists -or $envExists -ne $CONTAINER_APP_ENV) {
    Write-Host "   Environment not found. Creating Environment..." -ForegroundColor Yellow
    $envCreated = $false
    
    az containerapp env create --name $CONTAINER_APP_ENV --resource-group $RESOURCE_GROUP --location $LOCATION 2>&1 | Out-Null
    
    if ($LASTEXITCODE -eq 0) {
        $envCreated = $true
        Write-Host "   Environment created in region: $LOCATION" -ForegroundColor Green
    }
    
    if ($envCreated -eq $false) {
        Write-Host "   Failed in region $LOCATION. Trying other regions..." -ForegroundColor Yellow
        $altLocations = @("eastus", "westeurope", "centralus")
        
        foreach ($altLoc in $altLocations) {
            if ($altLoc -ne $LOCATION) {
                Write-Host "   Trying region: $altLoc" -ForegroundColor Yellow
                $LOCATION = $altLoc
                az containerapp env create --name $CONTAINER_APP_ENV --resource-group $RESOURCE_GROUP --location $LOCATION 2>&1 | Out-Null
                if ($LASTEXITCODE -eq 0) {
                    $envCreated = $true
                    Write-Host "   Environment created in region: $LOCATION" -ForegroundColor Green
                    break
                }
            }
        }
        
        if ($envCreated -eq $false) {
            Write-Host "   ERROR: Failed to create Environment in any region" -ForegroundColor Red
            exit 1
        }
    }
} else {
    Write-Host "   Environment found." -ForegroundColor Green
}

Write-Host ""
Write-Host "9. Creating Container App..." -ForegroundColor Yellow
$registryServer = $ACR_NAME + ".azurecr.io"
az containerapp create --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP --environment $CONTAINER_APP_ENV --image $fullImageName --registry-server $registryServer --registry-username $ACR_USERNAME --registry-password $ACR_PASSWORD --target-port 5000 --ingress external --min-replicas 1 --max-replicas 10 --cpu 0.5 --memory 1.0Gi --env-vars "DB_HOST=$DB_HOST" "DB_USER=$DB_USER" "DB_PASSWORD=$DB_PASSWORD" "DB_NAME=$DB_NAME" "PORT=5000"

Write-Host ""
Write-Host "10. Waiting for startup (30 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

Write-Host ""
Write-Host "11. Checking status..." -ForegroundColor Yellow
az containerapp show --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP --query "{name:name, status:properties.provisioningState, url:properties.configuration.ingress.fqdn}"

Write-Host ""
Write-Host "12. Checking logs..." -ForegroundColor Yellow
az containerapp logs show --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP --tail 50

Write-Host ""
Write-Host "13. Getting URL..." -ForegroundColor Yellow
$APP_URL = az containerapp show --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP --query properties.configuration.ingress.fqdn -o tsv

if ($APP_URL) {
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host "DEPLOYMENT COMPLETED!" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host "URL: https://$APP_URL" -ForegroundColor Yellow
    Write-Host "Swagger: https://$APP_URL/swagger/" -ForegroundColor Yellow
    Write-Host "API: https://$APP_URL/api/movies" -ForegroundColor Yellow
    Write-Host "==========================================" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "Error: URL not received. Check logs above." -ForegroundColor Red
}

Write-Host ""

