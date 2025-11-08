#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

if ! command -v az &> /dev/null; then
    error "Azure CLI is not installed. Install it: https://docs.microsoft.com/cli/azure/install-azure-cli"
fi

RESOURCE_GROUP="${RESOURCE_GROUP:-your-resource-group}"
LOCATION="westus"
ACR_NAME="${ACR_NAME:-your-acr-name}"
CONTAINER_APP_NAME="db-repo-app"
CONTAINER_APP_ENV="db-repo-env"
IMAGE_NAME="flask-rest-api"
IMAGE_TAG="latest"

DB_HOST="${DB_HOST:-your-db-server.mysql.database.azure.com}"
DB_USER="${DB_USER:-your_username}"
DB_PASSWORD="${DB_PASSWORD:-your_password}"
DB_NAME="${DB_NAME:-your_database_name}"

log "Starting Azure deployment..."

log "Checking Azure authentication..."
az account show &> /dev/null || az login

log "Registering resource providers..."
az provider register --namespace Microsoft.App --wait
az provider register --namespace Microsoft.OperationalInsights --wait
az provider register --namespace Microsoft.ContainerRegistry --wait
log "Resource providers registered"

log "Creating Resource Group: $RESOURCE_GROUP"
az group create --name $RESOURCE_GROUP --location $LOCATION --output none

log "Checking ACR existence: $ACR_NAME"
ACR_EXISTS=$(az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP 2>/dev/null)

if [ -z "$ACR_EXISTS" ]; then
    log "Creating new Azure Container Registry: $ACR_NAME"
    az acr create \
        --resource-group $RESOURCE_GROUP \
        --name $ACR_NAME \
        --sku Basic \
        --admin-enabled true \
        --output none
    
    if [ $? -ne 0 ]; then
        error "Failed to create ACR. Check if name '$ACR_NAME' is available (must be globally unique)"
    fi
    log "ACR created successfully"
else
    log "ACR already exists, using existing"
    az acr update --name $ACR_NAME --admin-enabled true --output none
fi

log "Logging into Azure Container Registry..."
az acr login --name $ACR_NAME

if [ $? -ne 0 ]; then
    error "Failed to login to ACR"
fi

log "Building Docker image for linux/amd64..."
docker buildx build --platform linux/amd64 -t ${ACR_NAME}.azurecr.io/${IMAGE_NAME}:${IMAGE_TAG} .

if [ $? -ne 0 ]; then
    warning "Buildx failed, trying regular build with --platform..."
    docker build --platform linux/amd64 -t ${ACR_NAME}.azurecr.io/${IMAGE_NAME}:${IMAGE_TAG} .
    
    if [ $? -ne 0 ]; then
        error "Failed to build Docker image"
    fi
fi
log "Docker image built successfully for linux/amd64"

log "Pushing image to Azure Container Registry..."
docker push ${ACR_NAME}.azurecr.io/${IMAGE_NAME}:${IMAGE_TAG}

if [ $? -ne 0 ]; then
    error "Failed to push image to ACR"
fi
log "Image successfully uploaded to ACR"

log "Getting ACR credentials..."
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username -o tsv 2>/dev/null)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query passwords[0].value -o tsv 2>/dev/null)

if [ -z "$ACR_USERNAME" ] || [ -z "$ACR_PASSWORD" ]; then
    error "Failed to get ACR credentials. Make sure admin-enabled=true"
fi
log "Credentials retrieved: $ACR_USERNAME"

log "Creating Container Apps Environment..."
ENV_EXISTS=$(az containerapp env show --name $CONTAINER_APP_ENV --resource-group $RESOURCE_GROUP 2>/dev/null)

if [ -z "$ENV_EXISTS" ]; then
    log "Creating new Environment..."
    az containerapp env create \
        --name $CONTAINER_APP_ENV \
        --resource-group $RESOURCE_GROUP \
        --location $LOCATION \
        --output none
    
    if [ $? -ne 0 ]; then
        error "Failed to create Container Apps Environment"
    fi
    log "Environment created successfully"
else
    log "Environment already exists, using existing"
fi

log "Checking Container App existence..."
APP_EXISTS=$(az containerapp show --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP 2>/dev/null)

if [ -n "$APP_EXISTS" ]; then
    warning "Container App already exists, deleting old one..."
    az containerapp delete \
        --name $CONTAINER_APP_NAME \
        --resource-group $RESOURCE_GROUP \
        --yes \
        --output none
    log "Old Container App deleted"
fi

log "Creating Container App with basic settings..."
az containerapp create \
    --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --environment $CONTAINER_APP_ENV \
    --image ${ACR_NAME}.azurecr.io/${IMAGE_NAME}:${IMAGE_TAG} \
    --registry-server ${ACR_NAME}.azurecr.io \
    --registry-username "$ACR_USERNAME" \
    --registry-password "$ACR_PASSWORD" \
    --target-port 5000 \
    --ingress external \
    --min-replicas 1 \
    --max-replicas 10 \
    --cpu 0.5 \
    --memory 1.0Gi \
    --env-vars \
        DB_HOST="$DB_HOST" \
        DB_USER="$DB_USER" \
        DB_PASSWORD="$DB_PASSWORD" \
        DB_NAME="$DB_NAME" \
        PORT=5000 \
    --output none

if [ $? -ne 0 ]; then
    error "Failed to create Container App"
fi
log "Container App created successfully"

log "Configuring auto-scaling rules..."

log "Adding CPU scaling rule (>70%)..."
az containerapp update \
    --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --min-replicas 1 \
    --max-replicas 10 \
    --scale-rule-name cpu-scaling \
    --scale-rule-type cpu \
    --scale-rule-metadata "utilization=70" \
    --output none

if [ $? -eq 0 ]; then
    log "CPU rule added successfully"
else
    warning "Failed to add CPU rule via CLI. You can configure it via Azure Portal."
fi

log "Adding Memory scaling rule (>80%)..."
MEMORY_RULE_FILE=$(mktemp)
cat > $MEMORY_RULE_FILE <<EOF
properties:
  template:
    scale:
      minReplicas: 1
      maxReplicas: 10
      rules:
        - name: cpu-scaling
          cpu:
            utilization: 70
        - name: memory-scaling
          memory:
            utilization: 80
EOF

az containerapp update \
    --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --yaml $MEMORY_RULE_FILE \
    --output none

if [ $? -eq 0 ]; then
    log "Memory rule added successfully"
else
    warning "Failed to add Memory rule via CLI. You can configure it via Azure Portal."
fi

rm -f $MEMORY_RULE_FILE

log "Auto-scaling rules configured:"
log "  - CPU: >70% usage (scale up)"
log "  - Memory: >80% usage (scale up)"
log "  - Min replicas: 1"
log "  - Max replicas: 10"
log ""
log "Note: If rules were not applied via CLI, configure them manually via Azure Portal:"
log "  Container App → Scale → Add scale rule"

log "Getting application URL..."
APP_URL=$(az containerapp show \
    --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query properties.configuration.ingress.fqdn -o tsv)

if [ -z "$APP_URL" ]; then
    warning "Failed to get application URL"
    APP_URL="unknown"
fi

log "=========================================="
log "Deployment completed successfully!"
log "=========================================="
log "Application URL: https://$APP_URL"
log "Swagger documentation: https://$APP_URL/api/docs/"
log "Resource Group: $RESOURCE_GROUP"
log "Container Registry: ${ACR_NAME}.azurecr.io"
log "Container App: $CONTAINER_APP_NAME"
log "=========================================="
log "Auto-scaling configured:"
log "  - Minimum: 1 instance"
log "  - Maximum: 10 instances"
log "  - CPU rule: >70%"
log "  - Memory rule: >80%"
log "=========================================="

echo "APP_URL=https://$APP_URL" > .env.azure
log "URL saved to .env.azure file"