#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

info() {
    echo -e "${BLUE}[MONITOR]${NC} $1"
}

RESOURCE_GROUP="${RESOURCE_GROUP:-your-resource-group}"
CONTAINER_APP_NAME="${CONTAINER_APP_NAME:-db-repo-app}"
MONITOR_INTERVAL="${MONITOR_INTERVAL:-10}"
LOG_FILE="${LOG_FILE:-scaling_monitor.log}"


if ! command -v az &> /dev/null; then
    error "Azure CLI is not installed. Install it: https://docs.microsoft.com/cli/azure/install-azure-cli"
    exit 1
fi


log "Checking Azure authentication..."
az account show &> /dev/null || {
    warning "Azure authentication required..."
    az login
}


get_replica_info() {
    local replicas=$(az containerapp replica list \
        --name $CONTAINER_APP_NAME \
        --resource-group $RESOURCE_GROUP \
        --query "[].{name:name, status:properties.runningState, created:properties.createdTime}" \
        -o json 2>/dev/null)
    
    if [ $? -eq 0 ] && [ -n "$replicas" ]; then
        echo "$replicas"
    else
        echo "[]"
    fi
}


get_metrics() {
    local end_time=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    local start_time=$(date -u -d "5 minutes ago" +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || date -u -v-5M +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null)
    
    local cpu_metrics=$(az monitor metrics list \
        --resource /subscriptions/$(az account show --query id -o tsv)/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.App/containerApps/$CONTAINER_APP_NAME \
        --metric "CpuPercentage" \
        --start-time "$start_time" \
        --end-time "$end_time" \
        --interval PT1M \
        --query "value[0].timeseries[0].data[-1].average" -o tsv 2>/dev/null)
    
    local memory_metrics=$(az monitor metrics list \
        --resource /subscriptions/$(az account show --query id -o tsv)/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.App/containerApps/$CONTAINER_APP_NAME \
        --metric "MemoryPercentage" \
        --start-time "$start_time" \
        --end-time "$end_time" \
        --interval PT1M \
        --query "value[0].timeseries[0].data[-1].average" -o tsv 2>/dev/null)
    
    echo "$cpu_metrics|$memory_metrics"
}


get_replica_count() {
    local count=$(az containerapp show \
        --name $CONTAINER_APP_NAME \
        --resource-group $RESOURCE_GROUP \
        --query "properties.template.scale.minReplicas" -o tsv 2>/dev/null)
    
    local actual_count=$(az containerapp replica list \
        --name $CONTAINER_APP_NAME \
        --resource-group $RESOURCE_GROUP \
        --query "length(@)" -o tsv 2>/dev/null)
    
    echo "$count|$actual_count"
}


log_to_file() {
    local message="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] $message" >> "$LOG_FILE"
}


monitor() {
    log "Starting monitoring for Container App: $CONTAINER_APP_NAME"
    log "Resource Group: $RESOURCE_GROUP"
    log "Monitoring interval: $MONITOR_INTERVAL seconds"
    log "Log file: $LOG_FILE"
    echo ""
    
    log_to_file "=== Monitoring started ==="
    
    while true; do
        local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
        
        local replica_info=$(get_replica_count)
        local min_replicas=$(echo "$replica_info" | cut -d'|' -f1)
        local actual_replicas=$(echo "$replica_info" | cut -d'|' -f2)
        
        local metrics=$(get_metrics)
        local cpu_usage=$(echo "$metrics" | cut -d'|' -f1)
        local memory_usage=$(echo "$metrics" | cut -d'|' -f2)
        
        echo "=========================================="
        info "Time: $timestamp"
        info "Replica count: $actual_replicas (min: $min_replicas)"
        
        if [ -n "$cpu_usage" ] && [ "$cpu_usage" != "null" ]; then
            printf "CPU usage: %.2f%%\n" "$cpu_usage"
            log_to_file "CPU: ${cpu_usage}%, Replicas: $actual_replicas"
        else
            echo "CPU usage: N/A"
        fi
        
        if [ -n "$memory_usage" ] && [ "$memory_usage" != "null" ]; then
            printf "Memory usage: %.2f%%\n" "$memory_usage"
            log_to_file "Memory: ${memory_usage}%, Replicas: $actual_replicas"
        else
            echo "Memory usage: N/A"
        fi
        
        local replicas_json=$(get_replica_info)
        if [ "$replicas_json" != "[]" ] && [ -n "$replicas_json" ]; then
            echo "Replicas:"
            echo "$replicas_json" | grep -o '"name":"[^"]*"' | sed 's/"name":"\(.*\)"/  - \1/' || echo "  No data"
        fi
        
        echo "=========================================="
        echo ""
        
        sleep $MONITOR_INTERVAL
    done
}

trap 'echo ""; log "Monitoring stopped"; log_to_file "=== Monitoring stopped ==="; exit 0' INT TERM

monitor

