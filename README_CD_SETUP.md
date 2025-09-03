# CD Setup Instructions

## Prerequisites

1. Enable required APIs in Google Cloud:
   ```bash
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable run.googleapis.com
   gcloud services enable containerregistry.googleapis.com
   ```

2. Create a service account for GitHub Actions:
   ```bash
   gcloud iam service-accounts create github-actions \
     --display-name="GitHub Actions Service Account"
   ```

3. Grant necessary permissions:
   ```bash
   PROJECT_ID=pitchperfect-lewagon
   
   gcloud projects add-iam-policy-binding $PROJECT_ID \
     --member="serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
     --role="roles/cloudbuild.builds.editor"
   
   gcloud projects add-iam-policy-binding $PROJECT_ID \
     --member="serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
     --role="roles/run.developer"
   
   gcloud projects add-iam-policy-binding $PROJECT_ID \
     --member="serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
     --role="roles/storage.admin"
   ```

4. Create and download service account key:
   ```bash
   gcloud iam service-accounts keys create key.json \
     --iam-account=github-actions@$PROJECT_ID.iam.gserviceaccount.com
   ```

5. Add the key to GitHub repository secrets:
   - Go to repository Settings > Secrets and variables > Actions
   - Create new secret named `GCP_SA_KEY`
   - Paste the entire contents of key.json
   - Delete the local key.json file

## How it works

1. When you push to master branch, GitHub Actions triggers the CD workflow
2. The workflow authenticates with Google Cloud using the service account
3. Cloud Build builds the Docker image and pushes to Container Registry
4. Cloud Build deploys the new image to Cloud Run

## Manual deployment

You can still use the existing deploy.sh script for manual deployments.