#!/bin/bash

# Docker Build and Test Script for Mojila Signal
# This script builds the Docker image and runs basic tests

set -e  # Exit on any error

echo "🐳 Building Mojila Signal Docker Image..."
echo "=========================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker and try again."
    exit 1
fi

# Build the Docker image
echo "📦 Building Docker image..."
docker build -t mojila-signal .

if [ $? -eq 0 ]; then
    echo "✅ Docker image built successfully!"
else
    echo "❌ Docker build failed!"
    exit 1
fi

# Test the image
echo "🧪 Testing Docker image..."
docker run --rm mojila-signal python test_installation.py

if [ $? -eq 0 ]; then
    echo "✅ Docker image test passed!"
else
    echo "❌ Docker image test failed!"
    exit 1
fi

echo ""
echo "🎉 Docker setup completed successfully!"
echo "=========================================="
echo "To run the application:"
echo "  docker-compose up --build"
echo ""
echo "To run with web interface:"
echo "  docker-compose --profile web up --build"
echo ""
echo "To run manually:"
echo "  docker run -d --name mojila-signal-app -p 5000:5000 mojila-signal"
echo ""
echo "For more information, see README-Docker.md"