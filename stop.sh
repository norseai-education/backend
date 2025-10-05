#!/bin/bash

# Stop the services using Docker Compose
docker-compose down

# Clean up unused Docker resources
docker system prune -f