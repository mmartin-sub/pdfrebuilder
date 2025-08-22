# Stage 1: Builder
FROM python:3.12-slim as builder

# Install uv
RUN pip install --no-cache-dir uv

# Set the working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml ./

# Install dependencies into a virtual environment
RUN uv venv /opt/venv
COPY . .
RUN /opt/venv/bin/uv pip install --no-cache --system -e .[all]

# Stage 2: Final Image
FROM python:3.12-slim

# Copy the virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy the application code
WORKDIR /app
COPY . .

# Set the PATH to include the virtual environment's bin directory
ENV PATH="/opt/venv/bin:$PATH"

# Set the entrypoint to the pdfrebuilder CLI
ENTRYPOINT ["pdfrebuilder"]

# Default command to show help
CMD ["--help"]
