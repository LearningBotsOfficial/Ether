# Use an official lightweight Python image
FROM python:3.11-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Set the working directory
WORKDIR /app

# Install only strictly necessary system dependencies
RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy pyproject.toml and uv.lock first to leverage Docker layer caching
COPY pyproject.toml uv.lock ./

# Install dependencies without installing the project itself
RUN uv sync --frozen --no-install-project

# Copy the rest of the application code
COPY . .

# Create persistent storage directories
RUN mkdir -p /app/media /app/sessions /app/logs && \
    chmod -R 777 /app/media /app/sessions /app/logs

# Define volumes for persistent data
VOLUME ["/app/media", "/app/sessions", "/app/logs"]

# Set the default command to run the application using uv run
CMD ["uv", "run", "main.py"]

