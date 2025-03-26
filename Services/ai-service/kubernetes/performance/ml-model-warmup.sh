#!/bin/bash

# Configuration
ENDPOINT="http://ai-service:5000"
MAX_RETRIES=3
RETRY_DELAY=5
LOG_FILE="/var/log/ml-model-warmup.log"

# Models to load
MODELS=(
    "recommendation_model"
    "sales_forecast_model"
)

# Logging function
log() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] $1" | tee -a "$LOG_FILE"
}

# Function to load a model with retry mechanism
load_model() {
    local model_name=$1
    local retry_count=0

    while [ $retry_count -lt $MAX_RETRIES ]; do
        log "Attempting to load model: $model_name (Attempt $((retry_count + 1))/$MAX_RETRIES)"
        
        response=$(curl -s -w "%{http_code}" -X POST "$ENDPOINT/load_model?name=$model_name")
        http_code=${response: -3}
        body=${response:0:${#response}-3}

        if [ "$http_code" -eq 200 ]; then
            log "Successfully loaded model: $model_name"
            return 0
        else
            log "Failed to load model: $model_name. HTTP Code: $http_code. Response: $body"
            ((retry_count++))
            
            if [ $retry_count -lt $MAX_RETRIES ]; then
                log "Retrying in $RETRY_DELAY seconds..."
                sleep $RETRY_DELAY
            fi
        fi
    done

    log "ERROR: Failed to load model $model_name after $MAX_RETRIES attempts"
    return 1
}

# Main execution
log "Starting model warmup process"

# Create log directory if it doesn't exist
mkdir -p $(dirname "$LOG_FILE")

# Check if service is available
if ! curl -s "$ENDPOINT/health" > /dev/null; then
    log "ERROR: AI service is not available"
    exit 1
fi

# Load each model
failed_models=0
for model in "${MODELS[@]}"; do
    if ! load_model "$model"; then
        ((failed_models++))
    fi
done

# Final status
log "Model warmup process completed"
if [ $failed_models -eq 0 ]; then
    log "All models loaded successfully"
    exit 0
else
    log "ERROR: Failed to load $failed_models model(s)"
    exit 1
fi
