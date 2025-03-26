FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies for OpenCV and other libraries
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt .

# Update pip and install dependencies with better timeout and retry settings
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --timeout=100 --retries=3 -r requirements.txt || \
    pip install --no-cache-dir --timeout=100 --retries=3 -r requirements.txt

# Copy application code
COPY app.py ./
COPY src/ ./src/
COPY config/ ./config/
COPY docs/ ./docs/
COPY interface/ ./interface/

# Create necessary directories with appropriate permissions
RUN mkdir -p data/secure_storage data/monitoring

# Copy main.py and other files
COPY main.py ./
COPY LICENSE ./
COPY CONTRIBUTING.md ./
COPY README.md ./

# Expose the port the app runs on
EXPOSE 5000

# Command to run the application
CMD ["python", "app.py"]
