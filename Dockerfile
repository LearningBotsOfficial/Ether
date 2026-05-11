# Use an official lightweight Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Set the working directory
WORKDIR /app

# Install system dependencies
# (git is often needed for some python packages or updates, build-essential for compiling wheels)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Create directories for media and sessions to avoid permission issues
# and mark them as volumes for persistence
RUN mkdir -p media sessions logs && \
    chmod -R 777 media sessions logs

# Define volumes for persistent data
VOLUME ["/app/media", "/app/sessions", "/app/logs"]

# Set the default command to run the application
CMD ["python", "main.py"]
