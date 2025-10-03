#!/bin/bash

# Quick Start Script for Vietnam Provinces API
# Run this on your Ubuntu 22.04 server

echo "🚀 Vietnam Provinces API - Quick Start"
echo "======================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    echo "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    echo "✅ Docker installed"
    echo "⚠️  Please log out and log back in for group changes to take effect"
    exit 0
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed"
    echo "Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo "✅ Docker Compose installed"
fi

echo ""
echo "✅ All dependencies installed"
echo ""

# Copy .env.example to .env if not exists
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "✅ .env file created"
fi

# Build and start
echo ""
echo "Building Docker image..."
docker-compose build

echo ""
echo "Starting containers..."
docker-compose up -d

echo ""
echo "Waiting for API to be ready..."
sleep 5

# Test API
echo ""
echo "Testing API..."
if curl -f http://localhost:8000/api/v2/ > /dev/null 2>&1; then
    echo "✅ API is running!"
    echo ""
    echo "🎉 Deployment successful!"
    echo ""
    echo "Access your API at:"
    echo "  - API v1: http://localhost:8000/api/v1/"
    echo "  - API v2: http://localhost:8000/api/v2/"
    echo "  - Docs: http://localhost:8000/docs"
    echo ""
    echo "Useful commands:"
    echo "  - View logs: docker-compose logs -f"
    echo "  - Stop: docker-compose down"
    echo "  - Restart: docker-compose restart"
else
    echo "❌ API failed to start"
    echo "Check logs with: docker-compose logs"
fi
