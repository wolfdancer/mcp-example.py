FROM python:3.10-slim

# Reduce vulnerabilities by updating system packages
RUN apt-get update && apt-get upgrade -y && apt-get clean

# Set the working directory
WORKDIR /app

# Copy the necessary files
COPY arxiv_server.py .
COPY pyproject.toml .

# Install required packages
RUN pip install --upgrade pip && pip install .

# Command to run the arxiv_server.py script
CMD ["python", "arxiv_server.py"]