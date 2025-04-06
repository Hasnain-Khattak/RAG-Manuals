#!/bin/bash

# Check if containers are running
if [ "$(docker compose ps --services --filter 'status=running' | wc -l)" -eq 0 ]; then
    echo "No containers running. Starting Docker containers..."
    docker compose up -d
else
    echo "Containers are already running..."
fi


# Run store-images.py to vectorize and save to SQLite
echo "Running store-images.py to vectorize the images..."
docker compose exec app python store-images.py 

# Check if the process was successful
if [ $? -eq 0 ]; then
    echo "store-images.py executed successfully."
else
    echo "store-images.py failed to run."
    exit 1
fi

# Now, stop the container
echo "Stopping Docker container..."
docker compose down

# Restart the container
echo "Restarting Docker container..."
docker compose up -d

# Check if everything is up and running
echo "Checking container status..."
docker compose ps

echo "Automation complete!"
