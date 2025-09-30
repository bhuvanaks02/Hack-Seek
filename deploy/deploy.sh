#!/bin/bash
# HackSeek Production Deployment Script

set -e  # Exit on any error

# Configuration
NAMESPACE="hackseek"
KUBECTL_CONTEXT=${KUBECTL_CONTEXT:-""}
DRY_RUN=${DRY_RUN:-false}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed or not in PATH"
        exit 1
    fi

    # Check cluster connection
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster"
        exit 1
    fi

    # Set context if provided
    if [[ -n "$KUBECTL_CONTEXT" ]]; then
        log_info "Setting kubectl context to $KUBECTL_CONTEXT"
        kubectl config use-context "$KUBECTL_CONTEXT"
    fi

    log_success "Prerequisites check passed"
}

# Apply Kubernetes manifests
apply_manifest() {
    local file=$1
    local description=$2

    log_info "Applying $description..."

    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "DRY RUN: Would apply $file"
        kubectl apply -f "$file" --dry-run=client
    else
        kubectl apply -f "$file"
        log_success "$description applied"
    fi
}

# Wait for deployment
wait_for_deployment() {
    local deployment=$1
    local timeout=${2:-300}

    log_info "Waiting for deployment $deployment to be ready..."

    if [[ "$DRY_RUN" == "false" ]]; then
        if kubectl rollout status deployment/"$deployment" -n "$NAMESPACE" --timeout="${timeout}s"; then
            log_success "Deployment $deployment is ready"
        else
            log_error "Deployment $deployment failed to become ready within ${timeout}s"
            return 1
        fi
    else
        log_info "DRY RUN: Would wait for deployment $deployment"
    fi
}

# Check deployment health
check_health() {
    log_info "Checking application health..."

    if [[ "$DRY_RUN" == "false" ]]; then
        # Check backend health
        if kubectl exec -n "$NAMESPACE" deployment/backend -- curl -f http://localhost:8000/health/ready; then
            log_success "Backend health check passed"
        else
            log_warning "Backend health check failed"
        fi

        # Check frontend accessibility
        if kubectl exec -n "$NAMESPACE" deployment/frontend -- curl -f http://localhost:3000/; then
            log_success "Frontend health check passed"
        else
            log_warning "Frontend health check failed"
        fi
    else
        log_info "DRY RUN: Would check application health"
    fi
}

# Main deployment function
deploy() {
    log_info "Starting HackSeek deployment to namespace: $NAMESPACE"

    # Create namespace
    apply_manifest "kubernetes/namespace.yaml" "namespace"

    # Apply secrets (make sure these are properly configured first)
    log_warning "Please ensure secrets are properly configured in kubernetes/secret.yaml"
    apply_manifest "kubernetes/secret.yaml" "secrets"

    # Apply configuration
    apply_manifest "kubernetes/configmap.yaml" "configuration"

    # Deploy database
    apply_manifest "kubernetes/postgres.yaml" "PostgreSQL database"
    wait_for_deployment "postgres" 600

    # Deploy Redis
    apply_manifest "kubernetes/redis.yaml" "Redis cache"
    wait_for_deployment "redis" 300

    # Deploy backend
    apply_manifest "kubernetes/backend.yaml" "backend application"
    wait_for_deployment "backend" 600

    # Deploy frontend
    apply_manifest "kubernetes/frontend.yaml" "frontend application"
    wait_for_deployment "frontend" 300

    # Apply ingress
    apply_manifest "kubernetes/ingress.yaml" "ingress configuration"

    # Check health
    sleep 30  # Give services time to start
    check_health

    log_success "Deployment completed successfully!"
}

# Rollback function
rollback() {
    local deployment=$1
    local revision=${2:-""}

    log_warning "Rolling back deployment: $deployment"

    if [[ -n "$revision" ]]; then
        kubectl rollout undo deployment/"$deployment" -n "$NAMESPACE" --to-revision="$revision"
    else
        kubectl rollout undo deployment/"$deployment" -n "$NAMESPACE"
    fi

    wait_for_deployment "$deployment"
    log_success "Rollback completed for $deployment"
}

# Status function
status() {
    log_info "Checking deployment status..."

    echo "Namespace: $NAMESPACE"
    echo
    echo "Pods:"
    kubectl get pods -n "$NAMESPACE"
    echo
    echo "Services:"
    kubectl get services -n "$NAMESPACE"
    echo
    echo "Ingresses:"
    kubectl get ingress -n "$NAMESPACE"
    echo
    echo "PVCs:"
    kubectl get pvc -n "$NAMESPACE"
}

# Logs function
logs() {
    local component=${1:-"backend"}
    local lines=${2:-100}

    log_info "Showing logs for $component (last $lines lines)..."
    kubectl logs -n "$NAMESPACE" deployment/"$component" --tail="$lines" -f
}

# Cleanup function
cleanup() {
    log_warning "This will delete all resources in namespace $NAMESPACE"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Deleting namespace $NAMESPACE..."
        kubectl delete namespace "$NAMESPACE"
        log_success "Cleanup completed"
    else
        log_info "Cleanup cancelled"
    fi
}

# Usage function
usage() {
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo
    echo "Commands:"
    echo "  deploy          Deploy the application"
    echo "  rollback        Rollback a deployment"
    echo "  status          Show deployment status"
    echo "  logs            Show application logs"
    echo "  cleanup         Delete all resources"
    echo "  help            Show this help message"
    echo
    echo "Options:"
    echo "  --dry-run       Perform a dry run without applying changes"
    echo "  --context       Kubernetes context to use"
    echo
    echo "Environment Variables:"
    echo "  KUBECTL_CONTEXT Set the kubectl context"
    echo "  DRY_RUN         Set to 'true' for dry run mode"
    echo
    echo "Examples:"
    echo "  $0 deploy"
    echo "  $0 deploy --dry-run"
    echo "  $0 rollback backend"
    echo "  $0 logs frontend 200"
    echo "  $0 status"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --context)
            KUBECTL_CONTEXT="$2"
            shift 2
            ;;
        *)
            break
            ;;
    esac
done

# Main command handling
case ${1:-deploy} in
    deploy)
        check_prerequisites
        deploy
        ;;
    rollback)
        check_prerequisites
        rollback "$2" "$3"
        ;;
    status)
        check_prerequisites
        status
        ;;
    logs)
        check_prerequisites
        logs "$2" "$3"
        ;;
    cleanup)
        check_prerequisites
        cleanup
        ;;
    help|--help|-h)
        usage
        ;;
    *)
        log_error "Unknown command: $1"
        usage
        exit 1
        ;;
esac