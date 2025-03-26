#!/bin/bash

# Script: export-helm-logs.sh
# Description: Advanced Helm logs exporter with error handling and configuration
# Author: Flowsale DevOps
# Version: 1.0.0

# Set strict error handling
set -euo pipefail

# Configuration variables
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly TIMESTAMP=$(date +%Y%m%d_%H%M%S)
readonly LOG_DIR="${SCRIPT_DIR}/logs"
readonly EXPORT_DIR="${SCRIPT_DIR}/exports"
readonly LOG_FILE="${LOG_DIR}/helm_export_${TIMESTAMP}.log"
readonly MAX_RETRIES=3
readonly TIMEOUT=300

# Color codes for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly NC='\033[0m' # No Color

# Function to log messages
log() {
    local level=$1
    local message=$2
    echo -e "[$(date +'%Y-%m-%d %H:%M:%S')] [${level}] ${message}" | tee -a "${LOG_FILE}"
}

# Function to handle errors
handle_error() {
    local exit_code=$?
    log "ERROR" "An error occurred on line $1 (exit code: ${exit_code})"
    cleanup
    exit ${exit_code}
}

# Set up error trap
trap 'handle_error $LINENO' ERR

# Function to clean up temporary files
cleanup() {
    log "INFO" "Performing cleanup..."
    rm -f /tmp/helm_export_*
}

# Function to check required tools
check_requirements() {
    local required_tools=("kubectl" "helm" "jq")
    
    for tool in "${required_tools[@]}"; do
        if ! command -v "${tool}" &> /dev/null; then
            log "ERROR" "${tool} is required but not installed. Please install it first."
            exit 1
        fi
    done
}

# Function to create necessary directories
initialize() {
    mkdir -p "${LOG_DIR}" "${EXPORT_DIR}"
    log "INFO" "Script initialized. Log file: ${LOG_FILE}"
}

# Function to get all namespaces with Helm releases
get_helm_namespaces() {
    kubectl get ns -o json | jq -r '.items[].metadata.name' | sort
}

# Function to export Helm release information
export_helm_release() {
    local namespace=$1
    local retry_count=0
    
    while [ ${retry_count} -lt ${MAX_RETRIES} ]; do
        if helm list -n "${namespace}" --output json > "${EXPORT_DIR}/helm_releases_${namespace}_${TIMESTAMP}.json" 2>>"${LOG_FILE}"; then
            log "INFO" "Successfully exported Helm releases for namespace: ${namespace}"
            return 0
        fi
        
        retry_count=$((retry_count + 1))
        log "WARN" "Retry ${retry_count}/${MAX_RETRIES} for namespace: ${namespace}"
        sleep 2
    done
    
    log "ERROR" "Failed to export Helm releases for namespace: ${namespace} after ${MAX_RETRIES} retries"
    return 1
}

# Main function
main() {
    log "INFO" "Starting Helm logs export process..."
    
    # Check requirements
    check_requirements
    
    # Initialize directories
    initialize
    
    # Set timeout for the entire operation
    timeout ${TIMEOUT} bash -c '
        # Get all namespaces
        namespaces=$(get_helm_namespaces)
        
        # Export Helm releases for each namespace
        for namespace in ${namespaces}; do
            export_helm_release "${namespace}" &
        done
        
        # Wait for all background processes to complete
        wait
    ' || log "ERROR" "Script execution timed out after ${TIMEOUT} seconds"
    
    # Create a summary report
    {
        echo "Helm Export Summary"
        echo "==================="
        echo "Date: $(date)"
        echo "Total namespaces processed: $(ls ${EXPORT_DIR}/helm_releases_*_${TIMESTAMP}.json 2>/dev/null | wc -l)"
        echo "Export location: ${EXPORT_DIR}"
    } > "${EXPORT_DIR}/summary_${TIMESTAMP}.txt"
    
    log "INFO" "Export completed successfully"
    
    # Cleanup
    cleanup
}

# Execute main function
main

exit 0