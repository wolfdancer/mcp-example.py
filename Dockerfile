FROM python:3.10-slim

# Reduce vulnerabilities by updating system packages (if needed)
RUN apt-get update && apt-get install -y --no-install-recommends curl && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml .

# Install required packages
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir .

# Copy application code
COPY arxiv_server.py .
# Command to run the arxiv_server.py script
CMD ["python", "arxiv_server.py"]