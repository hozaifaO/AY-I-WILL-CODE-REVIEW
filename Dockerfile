# Dockerfile
FROM python:3.10-slim

# Set working directory for app code
WORKDIR /app

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy action source code
COPY src/ ./src/

# Ensure Python can find the src package even when mounted at /github/workspace
ENV PYTHONPATH=/app

# Run the main module
ENTRYPOINT ["python", "-m", "src.main"]