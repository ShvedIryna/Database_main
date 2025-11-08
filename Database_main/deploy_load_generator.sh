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


RESOURCE_GROUP="${RESOURCE_GROUP:-your-resource-group}"
LOCATION="${LOCATION:-westus}"
ACR_NAME="${ACR_NAME:-your-acr-name}"
CONTAINER_APP_ENV="${CONTAINER_APP_ENV:-db-repo-env}"
LOAD_GENERATOR_APP_NAME="${LOAD_GENERATOR_APP_NAME:-load-generator-app}"
IMAGE_NAME="load-generator"
IMAGE_TAG="latest"


TARGET_URL="${TARGET_URL:-}"
THREADS="${THREADS:-20}"
DURATION="${DURATION:-600}"
RAMP_UP="${RAMP_UP:-60}"


if ! command -v az &> /dev/null; then
    error "Azure CLI is not installed. Install it: https://docs.microsoft.com/cli/azure/install-azure-cli"
fi


if [ -z "$TARGET_URL" ]; then
    error "TARGET_URL must be specified (URL of REST service for testing)"
fi

log "Starting load generator deployment..."


log "Checking Azure authentication..."
az account show &> /dev/null || az login


log "Logging into Azure Container Registry..."
az acr login --name $ACR_NAME

if [ $? -ne 0 ]; then
    error "Failed to login to ACR"
fi


log "Building Docker image for load generator..."
docker buildx build --platform linux/amd64 \
    -f Dockerfile.load_generator \
    -t ${ACR_NAME}.azurecr.io/${IMAGE_NAME}:${IMAGE_TAG} \
    . || docker build --platform linux/amd64 \
    -f Dockerfile.load_generator \
    -t ${ACR_NAME}.azurecr.io/${IMAGE_NAME}:${IMAGE_TAG} .

if [ $? -ne 0 ]; then
    error "Failed to build Docker image"
fi
log "Docker image built successfully"


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
    error "Failed to get ACR credentials"
fi


log "Checking Container Apps Environment..."
ENV_EXISTS=$(az containerapp env show --name $CONTAINER_APP_ENV --resource-group $RESOURCE_GROUP 2>/dev/null)

if [ -z "$ENV_EXISTS" ]; then
    error "Container Apps Environment '$CONTAINER_APP_ENV' does not exist. Run azure_deploy.sh first"
fi


log "Checking load generator Container App existence..."
APP_EXISTS=$(az containerapp show --name $LOAD_GENERATOR_APP_NAME --resource-group $RESOURCE_GROUP 2>/dev/null)

if [ -n "$APP_EXISTS" ]; then
    warning "Container App already exists, deleting old one..."
    az containerapp delete \
        --name $LOAD_GENERATOR_APP_NAME \
        --resource-group $RESOURCE_GROUP \
        --yes \
        --output none
    log "Old Container App deleted"
fi

log "Creating Container App for load generator..."
az containerapp create \
    --name $LOAD_GENERATOR_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --environment $CONTAINER_APP_ENV \
    --image ${ACR_NAME}.azurecr.io/${IMAGE_NAME}:${IMAGE_TAG} \
    --registry-server ${ACR_NAME}.azurecr.io \
    --registry-username "$ACR_USERNAME" \
    --registry-password "$ACR_PASSWORD" \
    --cpu 0.25 \
    --memory 0.5Gi \
    --min-replicas 1 \
    --max-replicas 1 \
    --env-vars \
        TARGET_URL="$TARGET_URL" \
        THREADS="$THREADS" \
        DURATION="$DURATION" \
        RAMP_UP="$RAMP_UP" \
    --command "python" \
    --args "load_generator.py" "--url" "$TARGET_URL" "--threads" "$THREADS" "--duration" "$DURATION" "--ramp-up" "$RAMP_UP" \
    --output none

if [ $? -ne 0 ]; then
    error "Failed to create Container App for load generator"
fi
log "Container App for load generator created successfully"

log "=========================================="
log "Load generator deployment completed!"
log "=========================================="
log "Container App: $LOAD_GENERATOR_APP_NAME"
log "Target URL: $TARGET_URL"
log "Threads: $THREADS"
log "Duration: $DURATION seconds"
log "Ramp-up: $RAMP_UP seconds"
log "=========================================="
log ""
log "To view logs, run:"
log "az containerapp logs show --name $LOAD_GENERATOR_APP_NAME --resource-group $RESOURCE_GROUP --follow"

