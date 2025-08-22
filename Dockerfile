# Stage 1: Builder
# Use ARG to make the Python version configurable
ARG PYTHON_VERSION=3.12
# Use a more specific base image tag for reproducibility
FROM python:${PYTHON_VERSION}-slim as builder

# Pin the uv version by copying the binary from the official image
# This is more reliable and addresses the pip pinning warning
COPY --from=ghcr.io/astral-sh/uv:0.1.33 /uv /usr/local/bin/uv

# Set the working directory
WORKDIR /app

# Create a virtual environment
# This step is cached and only re-runs if the base image changes
RUN uv venv /opt/venv

# Improve layer caching by copying only necessary files for dependency installation first
COPY pyproject.toml ./

# Install dependencies into the virtual environment
# This layer is only rebuilt when pyproject.toml changes
RUN /opt/venv/bin/uv pip install --no-cache --system -e '.[all]'

# Copy the rest of the application source code
COPY . .


# Stage 2: Final Image
ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION}-slim

# Create a non-root user and group for security
RUN addgroup --system app && adduser --system --ingroup app app

# Set environment variables
ENV VIRTUAL_ENV=/opt/venv
# The PATH is set once and includes the virtual environment's bin directory
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Copy the virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy the application code from the builder stage
WORKDIR /app
COPY --from=builder --chown=app:app /app .

# Switch to the non-root user
USER app

# Set the entrypoint to the pdfrebuilder CLI
ENTRYPOINT ["pdfrebuilder"]

# Default command to show help
CMD ["--help"]
