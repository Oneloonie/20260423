#!/bin/bash

# Exit on error
set -o errexit

# Install dependencies if needed (for Render/build environments)
# pip install -r requirements.txt

# Run the database setup script
python setup_db.py

# Run tests (optional during build)
# pytest

# Start the application (for local/docker)
# For Render, the startCommand in render.yaml will be used instead
uvicorn main:app --host 0.0.0.0 --port 8000
