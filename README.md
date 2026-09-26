# File Sharing System

A portfolio project for uploading, organising and sharing files through a web dashboard.

## What it does

- Register and sign in to a personal file workspace.
- Upload, filter, download and delete files; the dashboard groups files by type and shows storage usage.
- Generate public file links. Links do not expire automatically; the API supports owner-only deletion of a share.
- Store file metadata in PostgreSQL and file objects in S3-compatible storage. The Compose stack uses MinIO locally; the storage adapter also supports DigitalOcean Spaces.

## Stack

Vue 3, Vite, Pinia, FastAPI, SQLAlchemy, PostgreSQL, Alembic, MinIO / S3-compatible storage, Docker Compose.

## Run locally

Requires Docker Compose. From the repository root:

```sh
docker compose up --build
```

Open the dashboard at [http://localhost](http://localhost) and the FastAPI docs at [http://localhost:8000/docs](http://localhost:8000/docs).

## Backend tests

The backend test suite covers authentication, file operations, sharing, storage and core models. The GitHub Actions `test` workflow installs `backend/requirements.txt` and runs:

```sh
cd backend
pytest --tb=short -q
```

This repository describes the project code; it does not claim a currently hosted production service.
