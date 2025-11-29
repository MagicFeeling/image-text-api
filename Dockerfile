FROM python:3.11-slim

# Accept build arguments for user ID and group ID
ARG USER_ID=1000
ARG GROUP_ID=1000

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

# Create a non-root user with the same UID/GID as the host user
RUN groupadd -g ${GROUP_ID} appuser && \
    useradd -m -u ${USER_ID} -g ${GROUP_ID} -s /bin/bash appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Set the entrypoint
ENTRYPOINT ["python", "add_text_to_image.py"]
CMD ["config.json"]
