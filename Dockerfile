FROM python:3.10-slim

# Reduce vulnerabilities by updating system packages
RUN apt-get update && apt-get upgrade -y && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml .

# Install required packages
RUN pip install --upgrade pip && pip install .

# Copy application code
COPY arxiv_server.py .
# Command to run the arxiv_server.py script
CMD ["python", "arxiv_server.py"]