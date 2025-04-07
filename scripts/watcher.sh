#!/bin/bash

# Directory to watch
WATCH_DIR="/home/ubuntu/RAG-Manuals/Data"

# Ensure the watch directory exists
mkdir -p "$WATCH_DIR"

echo "Starting to watch $WATCH_DIR for new PDF files..."

# Watch for new files
inotifywait -m "$WATCH_DIR" -e create -e moved_to |
    while read path action file; do
        # Check if the file is a PDF
        if [[ "$file" =~ \.pdf$ ]]; then
            echo "New PDF detected: $file"
            echo "Starting image processing..."
            
            # Wait a moment to ensure file is completely uploaded
            sleep 2
            
            # Run the processing script
            /home/ubuntu/RAG-Manuals/scripts/process-images.sh
        fi
    done