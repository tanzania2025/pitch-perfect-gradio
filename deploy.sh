#!/bin/bash

# Pitch Perfect Frontend - Cloud Run Deployment Script

set -e

# Configuration
PROJECT_ID="pitchperfect-lewagon"
SERVICE_NAME="pitch-perfect-frontend"
REGION="europe-west1"  # Adjust based on your preference
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "🚀 Deploying Pitch Perfect Frontend to Cloud Run"
echo "Project: ${PROJECT_ID}"
echo "Service: ${SERVICE_NAME}"
echo "Region: ${REGION}"

# Authenticate with Google Cloud (if not already done)
echo "📋 Checking authentication..."
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -n1 > /dev/null; then
    echo "Please authenticate with Google Cloud:"
    gcloud auth login
fi

# Set the project
echo "🔧 Setting project..."
gcloud config set project ${PROJECT_ID}

# Enable required APIs
echo "🔌 Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable storage.googleapis.com

# Build the Docker image
echo "🏗️  Building Docker image..."
gcloud builds submit --tag ${IMAGE_NAME} .

# Deploy to Cloud Run
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME} \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 1 \
    --timeout 3600 \
    --concurrency 10 \
    --max-instances 10 \
    --set-env-vars ENVIRONMENT=production \
    --set-env-vars GCP_PROJECT_ID=${PROJECT_ID} \
    --set-env-vars GCS_BUCKET_NAME=pp-pitchperfect-lewagon-raw-data \
    --set-env-vars LOG_LEVEL=INFO

# Get the service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region=${REGION} --format="value(status.url)")

echo ""
echo "✅ Deployment completed successfully!"
echo "🌐 Your application is available at: ${SERVICE_URL}"
echo ""
echo "📋 Useful commands:"
echo "   View logs: gcloud run logs tail ${SERVICE_NAME} --region=${REGION}"
echo "   Update service: gcloud run services update ${SERVICE_NAME} --region=${REGION}"
echo "   Delete service: gcloud run services delete ${SERVICE_NAME} --region=${REGION}"
