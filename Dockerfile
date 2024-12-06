
#FROM python:3.12-slim

# Set working directory
#WORKDIR /app

# Copy application files
#COPY . /app

# Install system dependencies
#RUN apt-get update && apt-get install -y \
#    build-essential \
#    libssl-dev \
#    libffi-dev \
#    libmariadb-dev-compat \
#    libmariadb-dev \
#    pkg-config && \
#    rm -rf /var/lib/apt/lists/*

# Upgrade pip and setuptools
#RUN pip install --upgrade pip setuptools

# Install Python dependencies, excluding pywin32
#RUN grep -v "pywin32" requirements.txt > requirements-linux.txt && \
#    pip install --no-cache-dir -r requirements-linux.txt

# Expose the port your application uses (example: 5000)
#EXPOSE 5000

# Run your application (replace 'app.py' with your entrypoint file)
#CMD ["python", "app.py"]
#crate the docker file


# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    pkg-config \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install the project dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files into the container
COPY . .

# Set default environment variables
ENV DB_HOST=host.docker.internal
ENV DB_USERNAME=root
ENV DB_PASSWORD=W7301@jqir#
ENV DB_NAME=library_management_system

# Expose the port the app runs on
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Run the application
CMD ["flask", "run"]