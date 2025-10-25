.PHONY: help text install clean

# Default config file
CONFIG ?= config.json

help:
	@echo "Image Text API - Makefile Commands"
	@echo ""
	@echo "Usage:"
	@echo "  make text          - Add text overlays to images using config.json"
	@echo "  make text CONFIG=<file>  - Use custom config file"
	@echo "  make install       - Install Python dependencies"
	@echo "  make clean         - Remove Python cache files"
	@echo ""
	@echo "Examples:"
	@echo "  make text"
	@echo "  make text CONFIG=my_config.json"

text:
	@echo "Adding text to images..."
	python3 add_text_to_image.py $(CONFIG)

install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt

clean:
	@echo "Cleaning Python cache files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	@echo "Clean complete!"
