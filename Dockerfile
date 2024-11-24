FROM python:3.9-slim-bullseye

# Install Chrome and dependencies in a single layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Set display port and working directory
ENV DISPLAY=:99
WORKDIR /app

# Copy and install requirements first (for better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy only the necessary files
COPY script.py .

# Command to run the script
CMD ["python", "script.py"] 