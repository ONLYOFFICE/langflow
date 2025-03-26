#!/bin/bash

# Check if the onlyoffice network exists
if ! docker network inspect onlyoffice &> /dev/null; then
    echo "Creating onlyoffice network..."
    docker network create onlyoffice
else
    echo "onlyoffice network already exists."
fi

# Run docker-compose with the specified compose file
echo "Starting containers..."
docker compose -f dev.docker-compose.yml up -d

echo "Setup complete!"
