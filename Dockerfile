FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for PIL/Pillow
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir Pillow>=10.0.0

# Copy application files
COPY add_text_to_image.py /app/
COPY config.json /app/

# Set the entrypoint
ENTRYPOINT ["python", "add_text_to_image.py"]
CMD ["config.json"]
