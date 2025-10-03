.PHONY: help build up down restart logs ps clean test deploy

help:
	@echo "Vietnam Provinces API - Docker Commands"
	@echo "========================================"
	@echo "make build      - Build Docker image"
	@echo "make up         - Start containers"
	@echo "make down       - Stop containers"
	@echo "make restart    - Restart containers"
	@echo "make logs       - View logs"
	@echo "make ps         - Show container status"
	@echo "make clean      - Clean up Docker resources"
	@echo "make test       - Test API endpoints"
	@echo "make deploy     - Full deployment (build + up)"

build:
	docker-compose build

up:
	docker-compose up -d
	@echo "API is running at http://localhost:8000"
	@echo "Docs: http://localhost:8000/docs"

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

ps:
	docker-compose ps

clean:
	docker-compose down -v
	docker system prune -f

test:
	@echo "Testing API endpoints..."
	@curl -f http://localhost:8000/api/v2/ || echo "API not running"
	@curl -f http://localhost:8000/docs || echo "Docs not available"

deploy: build up
	@echo "Deployment complete!"
	@echo "Check status with: make ps"
	@echo "View logs with: make logs"
