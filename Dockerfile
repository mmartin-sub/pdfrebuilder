# Use an official, lean Python image as a base
FROM python:3.11-buster

# Install uv (fast Python package manager)
RUN pip install --no-cache-dir uv==0.8.4

# Set the working directory inside the container
WORKDIR /app

# Copy pyproject.toml and (optionally) pyproject.lock first for Docker layer caching
COPY pyproject.toml ./
COPY pyproject.lock ./

# Install Python dependencies using uv (from pyproject.toml)
RUN uv pip install --system --no-cache

# Copy all your project files into the container's working directory
COPY . .

# Set the command to run when the container starts, more for debugging
CMD ["python", "font_test2.py"]
