# Python REST API

This project contains a REST API built with FastAPI. It is hosted on Google Cloud Run and persists data in Firestore.

## Pre-requisites

- Python version 3.9
- Gcloud SDK

## Development

### Setup

Create a virtual environment and install dependencies

```bash
python -m venv venv
source venv/bin/activate

pip install -r requirements.txt
pip install -r requirements-test.txt
```

### Testing

Run unit tests

```bash
pytest tests --asyncio-mode=auto
```

### Running the application

Set environment variables

| Variable                | Description                         |
|-------------------------|-------------------------------------|
| PORT                    | Port for web server                 |
| FIRESTORE_EMULATOR_HOST | Host address for Firestore emulator |
| COLLECTION              | Firestore collection                |

Run application

```bash
# Start Firestore emulator
gcloud beta emulators firestore start --host-port ${FIRESTORE_EMULATOR_HOST}

# Start server
uvicorn app.main:app --port=${PORT}
```

### Calling the API

Set URL

```bash
export URL="localhost:${PORT}"
```

Call API

```bash
# Create new user
curl -i -X POST ${URL}/users/ \
-H "Content-Type: application/json" \
-d '{"first_name":"Jane","last_name":"Doe","email":"jane.doe@mail.com"}'

# Get user with id 'uid123'
curl -i -X GET ${URL}/users/uid123

# Get all users
curl -i -X GET ${URL}/users/

# Update user with id 'uid123'
curl -i -X PUT ${URL}/users/uid123 \
-H "Content-Type: application/json" \
-d '{"first_name":"Jane","last_name":"Doe","email":"jane@mail.com"}'

# Delete user with id 'uid123'
curl -i -X DELETE ${URL}/users/uid123
```

## Deployment

### Deploying to Cloud Run

Set environment variables

| Variable           | Description                                                                        |
|--------------------|------------------------------------------------------------------------------------|
| PROJECT            | GCP project                                                                        |
| REGION             | Region                                                                             |
| CLOUD_BUILD_BUCKET | Bucket used for Cloud Build                                                        |
| CLOUD_RUN_SA       | Email of service account used for Cloud Run. Needs the role `roles/datastore.user` |
| IMAGE              | Image tag                                                                          |
| SERVICE            | Service name                                                                       |
| COLLECTION         | Firestore collection                                                               |

Build container image with Cloud Build

```bash
gcloud builds submit . \
--project=${PROJECT} \
--config=./cloudbuild.yaml \
--gcs-source-staging-dir=gs://${CLOUD_BUILD_BUCKET}/staging \
--substitutions=_PROJECT=${PROJECT},_LOGS_BUCKET=${CLOUD_BUILD_BUCKET},_IMAGE=${IMAGE}
```

Deploy to Cloud Run

```bash
gcloud run deploy ${SERVICE} \
--project=${PROJECT} \
--region=${REGION} \
--image=eu.gcr.io/${PROJECT}/${IMAGE} \
--service-account=${CLOUD_RUN_SA} \
--update-env-vars=COLLECTION=${COLLECTION} \
--platform=managed \
--no-allow-unauthenticated
```

### Calling the API

Set URL and token

```bash
export URL=$(gcloud run services describe ${SERVICE} \
--project=${PROJECT} \
--region=${REGION} \
--format='value(status.url)')

export TOKEN=$(gcloud auth print-identity-token)
```

Call API

```bash
# Create new user
curl -i -X POST ${URL}/users/ \
-H "Authorization: Bearer ${TOKEN}" \
-H "Content-Type: application/json" \
-d '{"first_name":"Jane","last_name":"Doe","email":"jane.doe@mail.com"}'

# Get user with id 'uid123'
curl -i -X GET ${URL}/users/uid123 \
-H "Authorization: Bearer ${TOKEN}"

# Get all users
curl -i -X GET ${URL}/users/ \
-H "Authorization: Bearer ${TOKEN}"

# Update user with id 'uid123'
curl -i -X PUT ${URL}/users/uid123 \
-H "Authorization: Bearer ${TOKEN}" \
-H "Content-Type: application/json" \
-d '{"first_name":"Jane","last_name":"Doe","email":"jane@mail.com"}'

# Delete user with id 'uid123'
curl -i -X DELETE ${URL}/users/uid123 \
-H "Authorization: Bearer ${TOKEN}"
```
