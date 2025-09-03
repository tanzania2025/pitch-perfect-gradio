#!/bin/bash
# Simple deployment script for Pitch Perfect Gradio

set -e

# Load environment variables from .env
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Deployment configuration
SERVICE_NAME="pitch-perfect-frontend"
REPOSITORY="pitch-perfect-frontend-repo"
IMAGE_NAME="pitch-perfect-frontend"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

usage() {
    echo "Usage: $0 [local|gcp]"
    echo "  local  - Build and run locally with Docker"
    echo "  gcp    - Build, push to Artifact Registry, and deploy to Cloud Run"
    exit 1
}

local_deploy() {
    echo -e "${GREEN}🏠 Local Docker Deployment${NC}"

    echo "Building Docker image..."
    docker build -t ${IMAGE_NAME}:latest .

    echo "Running container locally..."
    docker run -d \
        --name ${IMAGE_NAME} \
        -p 7860:7860 \
        --env-file .env \
        ${IMAGE_NAME}:latest

    echo -e "${GREEN}✅ Local deployment complete!${NC}"
    echo -e "${YELLOW}Access your app at: http://localhost:7860${NC}"
    echo -e "${YELLOW}Stop with: docker stop ${IMAGE_NAME}${NC}"
}

gcp_deploy() {
    echo -e "${GREEN}☁️  Google Cloud Deployment${NC}"

    # Check if gcloud is authenticated
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -n1 > /dev/null; then
        echo -e "${RED}Please authenticate with gcloud first: gcloud auth login${NC}"
        exit 1
    fi

    # Set project
    gcloud config set project ${PROJECT_ID}

    # Enable APIs
    echo "Enabling required APIs..."
    gcloud services enable artifactregistry.googleapis.com
    gcloud services enable run.googleapis.com

    # Create Artifact Registry repository if it doesn't exist
    echo "Creating Artifact Registry repository..."
    gcloud artifacts repositories create ${REPOSITORY} \
        --repository-format=docker \
        --location=${REGION} \
        --description="Pitch Perfect containers" || true

    # Configure Docker for Artifact Registry
    gcloud auth configure-docker ${REGION}-docker.pkg.dev

    # Build image
    IMAGE_URI="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${IMAGE_NAME}:latest"
    echo "Building and pushing image to ${IMAGE_URI}..."

    docker build --platform linux/amd64 -t ${IMAGE_URI} .
    docker push ${IMAGE_URI}

    # Deploy to Cloud Run
    echo "Deploying to Cloud Run..."
    gcloud run deploy ${SERVICE_NAME} \
        --image ${IMAGE_URI} \
        --platform managed \
        --region ${REGION} \
        --allow-unauthenticated \
        --memory 2Gi \
        --cpu 1 \
        --timeout 300 \
        --max-instances 10 \
        --port 7860

    # Get service URL
    SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region=${REGION} --format="value(status.url)")

    echo -e "${GREEN}✅ GCP deployment complete!${NC}"
    echo -e "${YELLOW}Your app is available at: ${SERVICE_URL}${NC}"
}

cleanup_local() {
    echo "Cleaning up local containers..."
    docker stop ${IMAGE_NAME} 2>/dev/null || true
    docker rm ${IMAGE_NAME} 2>/dev/null || true
}

# Main script
case "${1:-}" in
    "local")
        cleanup_local
        local_deploy
        ;;
    "gcp")
        gcp_deploy
        ;;
    "clean")
        cleanup_local
        echo "Local cleanup complete"
        ;;
    *)
        usage
        ;;
esac
