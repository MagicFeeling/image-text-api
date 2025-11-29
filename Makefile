.PHONY: help text build clean down logs

# Default config file
CONFIG ?= config.json

help:
	@echo "Image Text API - Makefile Commands"
	@echo ""
	@echo "Usage:"
	@echo "  make text          - Run image text overlay in Docker"
	@echo "  make build         - Build Docker image"
	@echo "  make clean         - Remove Docker containers and images"
	@echo "  make down          - Stop and remove containers"
	@echo "  make logs          - Show container logs"
	@echo ""
	@echo "Examples:"
	@echo "  make text"

text:
	@echo "Running image-text-api in Docker..."
	docker compose up --build

build:
	@echo "Building Docker image..."
	docker compose build

down:
	@echo "Stopping containers..."
	docker compose down

clean:
	@echo "Cleaning up Docker resources..."
	docker compose down --rmi all --volumes
	@echo "Clean complete!"

logs:
	@echo "Showing logs..."
	docker compose logs -f
