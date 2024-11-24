FROM python:3.9-slim-bullseye

# Install Chrome and dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    chromium-driver \
    xvfb \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Set timezone
ENV TZ=America/Chicago
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Set display port and Chrome options
ENV DISPLAY=:99
ENV CHROME_BIN=/usr/bin/chromium

WORKDIR /app

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the script
COPY script.py .

# Command to run with xvfb
CMD ["python", "script.py"] 