#!/bin/bash

# Load environment variables from .env file
if [ -f .env ]; then
    export $(cat home/ubuntu/RAG-Manuals/.env | grep -v '^#' | xargs)
else
    echo "Error: .env file not found"
    exit 1
fi

# Check if DOMAIN_NAME is set
if [ -z "$DOMAIN_NAME" ]; then
    echo "Error: DOMAIN_NAME not set in .env file"
    exit 1
fi

# Install certbot
sudo apt-get update
sudo apt-get install -y certbot

# Get SSL certificate
echo "Getting SSL certificate for domain: $DOMAIN_NAME"
sudo certbot certonly --standalone -d $DOMAIN_NAME -d www.$DOMAIN_NAME