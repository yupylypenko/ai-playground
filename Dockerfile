# Dockerfile for Cosmic Flight Simulator
#
# Builds a containerized version of the application that runs the FastAPI server.
# The API server runs on port 8000 by default.
#
# Usage:
#     # Build the image
#     docker build -t cosmic-flight-simulator .
#
#     # Run the API server
#     docker run -p 8000:8000 cosmic-flight-simulator
#
#     # Run with custom port
#     docker run -p 3000:8000 cosmic-flight-simulator
#
#     # Run with environment variables
#     docker run -p 8000:8000 -e MONGODB_URI=mongodb://host:27017 cosmic-flight-simulator
#
#     # Run main.py CLI instead of API
#     docker run cosmic-flight-simulator python main.py --test-only

# Use Python 3.11+ as specified in .cursorrules
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
# Note: PyOpenGL and pygame may require additional system libraries
# For headless operation, we install minimal dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port 8000 for the FastAPI server
EXPOSE 8000

# Default command: run the FastAPI API server
# Users can override this to run main.py or other commands
CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
