#!/bin/bash

echo "Starting the automation script..."

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Check if containers are running
if [ "$(docker compose ps --services --filter 'status=running' | wc -l)" -eq 0 ]; then
    echo "No containers running. Starting Docker containers..."
    docker compose up -d
    # Wait for containers to be ready (increase sleep time)
    sleep 20
fi

# Run store-images.py to vectorize and save to SQLite
echo "Running store-images.py to vectorize the images..."
docker compose exec -T app python store-images.py 

# Check if the process was successful
if [ $? -eq 0 ]; then
    echo "store-images.py executed successfully."
    
    # Restart containers if needed
    echo "Restarting containers..."
    docker compose down
    docker compose up -d
    
else
    echo "store-images.py failed to run."
    exit 1
fi

echo "Processing complete!"