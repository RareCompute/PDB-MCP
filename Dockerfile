# Use an official Python runtime as a parent image
FROM python:3.11-slim-bullseye

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Create a non-root user and group
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin -c "Docker image user" appuser

# Install system dependencies (if any were needed, e.g., for certain Python packages)
# RUN apt-get update && apt-get install -y --no-install-recommends some-package && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
# Ensure the mcp_pdb directory from the host is copied into /app/mcp_pdb in the container
COPY ./mcp_pdb /app/mcp_pdb

# Change ownership of the app directory to the non-root user
RUN chown -R appuser:appuser /app

# Switch to the non-root user
USER appuser

# Expose port 8000 to the outside world
EXPOSE 8000

# Command to run the application
# Ensure the path to the app (mcp_pdb.main:app) is correct based on WORKDIR and COPY
CMD ["uvicorn", "mcp_pdb.main:app", "--host", "0.0.0.0", "--port", "8000"]
