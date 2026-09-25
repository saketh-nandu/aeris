#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="${PROJECT_ID:-ai-e-r-i-s}"
REGION="${REGION:-us-central1}"
SERVICE_NAME="${SERVICE_NAME:-aeris-backend}"
IMAGE="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

if ! command -v gcloud >/dev/null 2>&1; then
  echo "gcloud CLI is required but not installed. Install it first: https://cloud.google.com/sdk/docs/install"
  exit 1
fi

if ! gcloud auth list --filter=status:ACTIVE --format='value(account)' | grep -q .; then
  echo "You are not logged into gcloud. Run: gcloud auth login"
  exit 1
fi

gcloud config set project "${PROJECT_ID}"

docker build -t "${IMAGE}:latest" .
docker push "${IMAGE}:latest"

gcloud run deploy "${SERVICE_NAME}" \
  --image "${IMAGE}:latest" \
  --platform managed \
  --region "${REGION}" \
  --allow-unauthenticated \
  --project "${PROJECT_ID}"

echo "Deployment complete. Set VITE_API_BASE_URL to the Cloud Run URL shown above."
