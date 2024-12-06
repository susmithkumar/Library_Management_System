FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy application files
COPY . /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    libmariadb-dev-compat \
    libmariadb-dev \
    pkg-config && \
    rm -rf /var/lib/apt/lists/*

# Upgrade pip and setuptools
RUN pip install --upgrade pip setuptools

# Install Python dependencies, excluding pywin32
RUN grep -v "pywin32" requirements.txt > requirements-linux.txt && \
    pip install --no-cache-dir -r requirements-linux.txt

# Expose the port your application uses (example: 5000)
EXPOSE 5000

# Run your application (replace 'app.py' with your entrypoint file)
CMD ["python", "app.py"]
#crate the docker file